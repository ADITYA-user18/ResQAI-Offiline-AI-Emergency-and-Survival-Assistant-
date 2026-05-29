"""
utils/logger.py — ResQAI Centralized Logging System
=====================================================
Provides a single configured logger used across all backend modules.
Writes to both console and a rotating log file.
"""

import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path

# Import config without circular imports by reading values directly
try:
    from config import LOG_LEVEL, LOG_FILE, LOG_MAX_BYTES, LOG_BACKUP_COUNT, LOGS_DIR
except ImportError:
    # Fallback if run standalone
    LOG_LEVEL      = "INFO"
    LOG_FILE       = Path("logs/resqai_backend.log")
    LOG_MAX_BYTES  = 5 * 1024 * 1024
    LOG_BACKUP_COUNT = 3
    LOGS_DIR       = Path("logs")

# ─────────────────────────────────────────────────────────────────────────────

def get_logger(name: str = "resqai") -> logging.Logger:
    """
    Return a named logger with both console and file handlers.

    Usage:
        from utils.logger import get_logger
        logger = get_logger(__name__)
        logger.info("Server started")
    """
    logger = logging.getLogger(name)

    # Avoid adding duplicate handlers on repeated calls
    if logger.handlers:
        return logger

    logger.setLevel(getattr(logging, LOG_LEVEL.upper(), logging.INFO))

    # ── Formatter ─────────────────────────────────────────────────────────────
    fmt = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # ── Console handler ────────────────────────────────────────────────────────
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(fmt)
    logger.addHandler(console_handler)

    # ── Rotating file handler ──────────────────────────────────────────────────
    try:
        LOGS_DIR.mkdir(parents=True, exist_ok=True)
        file_handler = RotatingFileHandler(
            filename=LOG_FILE,
            maxBytes=LOG_MAX_BYTES,
            backupCount=LOG_BACKUP_COUNT,
            encoding="utf-8",
        )
        file_handler.setFormatter(fmt)
        logger.addHandler(file_handler)
    except Exception as e:
        logger.warning(f"Could not set up file logging: {e}")

    return logger


# ── Module-level default logger ──────────────────────────────────────────────
logger = get_logger("resqai")
