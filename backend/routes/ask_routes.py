"""
routes/ask_routes.py — /ask Endpoint (Authenticated RAG Pipeline)
=================================================================
Handles the primary user interaction.
Now requires JWT authentication — each ask is tied to the logged-in user.

POST /ask — Accept a query, run RAG, return AI response.

Full request lifecycle:
  1. Validate JWT → extract current_user
  2. Validate request body (Pydantic)
  3. Get or create chat session scoped to current_user.user_id
  4. Save user message (SQLite)
  5. Embed query (Ollama nomic-embed-text)
  6. Retrieve top-K chunks (FAISS)
  7. Fetch full texts (KnowledgeService)
  8. Get conversation history (SQLite)
  9. Build prompt (PromptBuilder)
  10. Generate response (Ollama LLM)
  11. Save assistant response (SQLite)
  12. Return structured JSON
"""
import json
from fastapi import APIRouter
from fastapi.responses import StreamingResponse

try:
    from models.request_models   import AskRequest
    from models.response_models  import AskResponse, SourceModel, ChunkModel
    from services.chat_service   import chat_service
    from services.ollama_service import ollama_service
    from rag.retriever           import retrieve
    from rag.prompt_builder      import build_prompt, build_system_prompt
    from utils.helpers           import sanitize_query
    from utils.logger            import get_logger
    from config                  import TOP_K_RESULTS, OLLAMA_STREAM
    from auth.auth_handler       import AuthDep
except ImportError as e:
    raise ImportError(f"ask_routes import error: {e}")

logger = get_logger(__name__)
router = APIRouter(tags=["Ask"])


@router.post(
    "/ask",
    response_model=AskResponse,
    summary="Ask an emergency question (authenticated)",
    description=(
        "Submit an emergency question. Requires JWT in Authorization header. "
        "The response is tied to your account — your chat history is private. "
        "Pass `chat_id` to continue an existing conversation."
    ),
)
async def ask(request: AskRequest, current_user: AuthDep) -> AskResponse:
    """
    Core RAG endpoint — authenticated and per-user isolated.
    current_user is injected by FastAPI from the validated JWT.
    """
    # ── Step 1: Sanitize query ────────────────────────────────────────────────
    clean_query = sanitize_query(request.query)
    logger.info(
        f"[/ask] user='{current_user.username}' query='{clean_query[:80]}'"
    )

    # ── Step 2: Get or create chat session (scoped to this user) ──────────────
    chat = chat_service.get_or_create_chat(
        user_id=current_user.user_id,
        chat_id=request.chat_id,
        first_query=clean_query,
    )
    chat_id = chat["chat_id"]
    logger.debug(f"[/ask] Using chat: {chat_id}")

    # ── Step 3: Save user message ─────────────────────────────────────────────
    chat_service.save_user_message(chat_id=chat_id, content=clean_query)

    # ── Step 4–6: Semantic retrieval pipeline ─────────────────────────────────
    try:
        chunks = retrieve(clean_query, top_k=TOP_K_RESULTS)
    except ConnectionError as e:
        logger.error(f"[/ask] Embedding failed: {e}")
        fallback_answer = (
            "I'm unable to search the knowledge base right now because "
            "the embedding service is not available. "
            "Please ensure Ollama is running: `ollama serve`"
        )
        chat_service.save_assistant_message(chat_id=chat_id, content=fallback_answer)
        return AskResponse(
            chat_id=chat_id,
            answer=fallback_answer,
            sources=[],
            retrieved_chunks=[],
        )

    # ── Step 7: Get conversation history for context ──────────────────────────
    history = chat_service.get_recent_context(chat_id)
    history = [
        m for m in history
        if not (m.get("role") == "user" and m.get("content") == clean_query)
    ]

    # ── Step 8: Build prompt ──────────────────────────────────────────────────
    prompt = build_prompt(
        query=clean_query,
        chunks=chunks,
        chat_history=history,
    )

    # ── Step 11: Build response ───────────────────────────────────────────────
    sources = [
        SourceModel(
            id=c.chunk_id,
            title=c.title,
            category=c.category,
            priority=c.priority,
            source=c.source,
        )
        for c in chunks
    ]

    retrieved_chunks = [
        ChunkModel(
            chunk_id=c.chunk_id,
            title=c.title,
            category=c.category,
            priority=c.priority,
            source=c.source,
            text=c.text,
            distance=c.distance,
        )
        for c in chunks
    ]

    if OLLAMA_STREAM:
        async def event_generator():
            # 1. Send metadata first
            meta = {
                "type": "metadata",
                "chat_id": chat_id,
                "sources": [s.model_dump() for s in sources],
                "retrieved_chunks": [c.model_dump() for c in retrieved_chunks],
            }
            yield f"data: {json.dumps(meta)}\n\n"
            
            # 2. Stream generation
            full_answer = ""
            try:
                for token in ollama_service.generate_stream(prompt=prompt, system_prompt=build_system_prompt()):
                    full_answer += token
                    yield f"data: {json.dumps({'type': 'chunk', 'content': token})}\n\n"
            except Exception as e:
                logger.error(f"[/ask] Stream generation failed: {e}")
                err_msg = "\n[Error: Connection interrupted]"
                full_answer += err_msg
                yield f"data: {json.dumps({'type': 'chunk', 'content': err_msg})}\n\n"
                
            # 3. Save to DB and close
            chat_service.save_assistant_message(chat_id=chat_id, content=full_answer)
            yield f"data: {json.dumps({'type': 'done'})}\n\n"
            
        return StreamingResponse(event_generator(), media_type="text/event-stream")

    else:
        # Standard synchronous path
        try:
            answer = ollama_service.generate(
                prompt=prompt,
                system_prompt=build_system_prompt(),
            )
        except (ConnectionError, TimeoutError) as e:
            logger.error(f"[/ask] LLM generation failed: {e}")
            answer = (
                "The AI model is currently unavailable. "
                "Based on retrieved knowledge, here is what was found:\n\n"
                + "\n\n".join(
                    f"• {c.title}: {c.text[:300]}..." for c in chunks[:2]
                )
                if chunks else
                "No knowledge was retrieved and the AI model is unavailable."
            )

        logger.info(
            f"[/ask] Answer ({len(answer)} chars) for user='{current_user.username}' chat={chat_id}"
        )

        chat_service.save_assistant_message(chat_id=chat_id, content=answer)

        return AskResponse(
            chat_id=chat_id,
            answer=answer,
            sources=sources,
            retrieved_chunks=retrieved_chunks,
        )
