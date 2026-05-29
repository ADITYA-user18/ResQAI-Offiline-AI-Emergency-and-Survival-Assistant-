"""
routes/auth_routes.py — Signup / Login / Logout / Me
=====================================================
All auth endpoints. 100% offline — no external services.

POST /signup  — Register a new local user account
POST /login   — Authenticate and receive a JWT
POST /logout  — Client-side logout (token invalidation note below)
GET  /me      — Get current user's profile (requires valid JWT)

Offline auth model:
    Credentials verified against local SQLite → JWT signed with local key
    → Client stores JWT → Client sends JWT on every request → Server
    validates JWT signature locally (no network call needed)
"""

import sqlite3
from fastapi import APIRouter, HTTPException, status

try:
    from models.request_models  import SignupRequest, LoginRequest
    from models.response_models import AuthResponse, UserPublicModel, MeResponse, LogoutResponse
    from database.chat_db       import (
        create_user, get_user_by_username, get_user_by_id,
        username_exists, update_last_login,
    )
    from auth.password_handler  import hash_password, verify_password
    from auth.jwt_handler       import create_access_token
    from auth.auth_handler      import get_current_user, CurrentUser, AuthDep
    from utils.helpers          import generate_uuid
    from utils.logger           import get_logger
except ImportError as e:
    raise ImportError(f"auth_routes import error: {e}")

logger = get_logger(__name__)
router = APIRouter(tags=["Authentication"], prefix="/auth")


# ─────────────────────────────────────────────────────────────────────────────
# POST /auth/signup
# ─────────────────────────────────────────────────────────────────────────────

@router.post(
    "/signup",
    response_model=AuthResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user account",
    description=(
        "Creates a new local user account and returns a JWT access token. "
        "Works fully offline — credentials are stored in local SQLite. "
        "Username must be unique and alphanumeric (3–30 chars)."
    ),
)
async def signup(request: SignupRequest) -> AuthResponse:
    """
    Registration flow:
        1. Check username uniqueness
        2. Hash password with bcrypt
        3. Insert into users table
        4. Sign and return JWT
    """
    logger.info(f"[/auth/signup] Signup attempt for username: '{request.username}'")

    # ── Step 1: Username uniqueness check ─────────────────────────────────────
    if username_exists(request.username):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Username '{request.username}' is already taken. Choose another.",
        )

    # ── Step 2: Hash password (bcrypt — never store plain text) ───────────────
    password_hash = hash_password(request.password)

    # ── Step 3: Create user in SQLite ─────────────────────────────────────────
    user_id = generate_uuid()
    try:
        user = create_user(
            user_id=user_id,
            username=request.username,
            password_hash=password_hash,
            device_id=request.device_id,
        )
    except sqlite3.IntegrityError:
        # Race condition: another request created the same username
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username already taken.",
        )

    # ── Step 4: Create JWT ────────────────────────────────────────────────────
    token = create_access_token(user_id=user_id, username=user["username"])

    logger.info(f"[/auth/signup] User registered: '{user['username']}' ({user_id})")

    return AuthResponse(
        access_token=token,
        token_type="Bearer",
        user=UserPublicModel(**user),
    )


# ─────────────────────────────────────────────────────────────────────────────
# POST /auth/login
# ─────────────────────────────────────────────────────────────────────────────

@router.post(
    "/login",
    response_model=AuthResponse,
    summary="Login to an existing account",
    description=(
        "Authenticates a user against local SQLite credentials. "
        "Returns a JWT access token valid for 30 days. "
        "Works fully offline — no internet required."
    ),
)
async def login(request: LoginRequest) -> AuthResponse:
    """
    Login flow:
        1. Look up user by username
        2. Verify password hash (bcrypt constant-time comparison)
        3. Update last_login timestamp
        4. Sign and return JWT
    """
    logger.info(f"[/auth/login] Login attempt for username: '{request.username}'")

    # ── Step 1: Look up user ──────────────────────────────────────────────────
    user = get_user_by_username(request.username)

    # Use the same generic error for both "user not found" and "wrong password"
    # to prevent username enumeration attacks.
    auth_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid username or password.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if not user:
        logger.warning(f"[/auth/login] Unknown username: '{request.username}'")
        raise auth_error

    # ── Step 2: Verify password ───────────────────────────────────────────────
    if not verify_password(request.password, user["password_hash"]):
        logger.warning(f"[/auth/login] Wrong password for: '{request.username}'")
        raise auth_error

    # ── Step 3: Update last_login ─────────────────────────────────────────────
    update_last_login(user["user_id"])

    # ── Step 4: Create JWT ────────────────────────────────────────────────────
    token = create_access_token(
        user_id=user["user_id"],
        username=user["username"],
    )

    logger.info(f"[/auth/login] Successful login: '{user['username']}'")

    # Build response — exclude password_hash
    public_user = UserPublicModel(
        user_id    = user["user_id"],
        username   = user["username"],
        created_at = user["created_at"],
        last_login = user.get("last_login"),
        device_id  = user.get("device_id"),
    )

    return AuthResponse(
        access_token=token,
        token_type="Bearer",
        user=public_user,
    )


# ─────────────────────────────────────────────────────────────────────────────
# POST /auth/logout
# ─────────────────────────────────────────────────────────────────────────────

@router.post(
    "/logout",
    response_model=LogoutResponse,
    summary="Logout (client-side token removal)",
    description=(
        "Stateless logout: the server confirms the token is valid, "
        "then the client must delete the stored token from localStorage. "
        "For full token revocation in future phases, implement a server-side "
        "token blacklist table in SQLite."
    ),
)
async def logout(current_user: AuthDep) -> LogoutResponse:
    """
    Stateless JWT logout.

    Note: JWTs are stateless by design — the server cannot truly invalidate
    a token once issued without a revocation list. For offline use, this is
    acceptable. The client must delete the stored token after logout.

    Future enhancement: add a `revoked_tokens` SQLite table.
    """
    logger.info(f"[/auth/logout] User logged out: '{current_user.username}'")
    return LogoutResponse(
        success=True,
        message=(
            "Logged out successfully. "
            "Please delete the access token from your device storage."
        ),
    )


# ─────────────────────────────────────────────────────────────────────────────
# GET /auth/me
# ─────────────────────────────────────────────────────────────────────────────

@router.get(
    "/me",
    response_model=MeResponse,
    summary="Get current user profile",
    description=(
        "Returns the authenticated user's profile information. "
        "Requires a valid JWT in the Authorization header."
    ),
)
async def get_me(current_user: AuthDep) -> MeResponse:
    """Return the current authenticated user's public profile."""
    user = get_user_by_id(current_user.user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User account not found. It may have been deleted.",
        )

    return MeResponse(user=UserPublicModel(**user))
