"""
rag/embeddings.py — Query Embedding Generator
=============================================
Generates vector embeddings for user queries using Ollama's
nomic-embed-text model (same model used to build the FAISS index).

CRITICAL: The embedding model MUST match the one used during indexing.
DO NOT change EMBEDDING_MODEL without rebuilding the FAISS index.
"""

import numpy as np
import requests
import json
from typing import Optional

try:
    from config import OLLAMA_BASE_URL, EMBEDDING_MODEL, OLLAMA_TIMEOUT_SEC
    from utils.logger import get_logger
except ImportError:
    OLLAMA_BASE_URL    = "http://localhost:11434"
    EMBEDDING_MODEL    = "nomic-embed-text"
    OLLAMA_TIMEOUT_SEC = 120
    import logging
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger(__name__)

# Ollama embedding endpoint
EMBED_URL = f"{OLLAMA_BASE_URL}/api/embed"


def embed_query(text: str) -> np.ndarray:
    """
    Generate a float32 embedding vector for the input text using Ollama.

    Uses the same nomic-embed-text model that was used when building
    the FAISS index, ensuring vector space compatibility.

    Args:
        text: The user's query string (already sanitized).

    Returns:
        1D numpy array of float32 values (e.g., shape (768,)).

    Raises:
        ConnectionError: If Ollama is unreachable.
        RuntimeError:    If embedding generation fails.
        ValueError:      If the returned embedding is malformed.
    """
    if not text or not text.strip():
        raise ValueError("Cannot embed empty text")

    payload = {
        "model":  EMBEDDING_MODEL,
        "input": text.strip(),
    }

    logger.debug(f"Requesting embedding for: '{text[:80]}...'")

    try:
        response = requests.post(
            EMBED_URL,
            json=payload,
            timeout=OLLAMA_TIMEOUT_SEC,
        )
        response.raise_for_status()
    except requests.exceptions.ConnectionError:
        raise ConnectionError(
            f"Cannot reach Ollama at {OLLAMA_BASE_URL}. "
            "Ensure Ollama is running: `ollama serve`"
        )
    except requests.exceptions.Timeout:
        raise TimeoutError(
            f"Ollama embedding timed out after {OLLAMA_TIMEOUT_SEC}s"
        )
    except requests.exceptions.HTTPError as e:
        raise RuntimeError(f"Embedding API returned error: {e}") from e

    try:
        data = response.json()
    except json.JSONDecodeError as e:
        raise RuntimeError(f"Invalid JSON from embedding API: {e}") from e

    embeddings = data.get("embeddings")
    if not embeddings or not isinstance(embeddings, list) or len(embeddings) == 0:
        raise ValueError(
            f"Empty embedding returned by Ollama. "
            f"Ensure '{EMBEDDING_MODEL}' is pulled: `ollama pull {EMBEDDING_MODEL}`"
        )
    embedding = embeddings[0]

    vector = np.array(embedding, dtype=np.float32)
    logger.debug(f"Embedding generated: shape={vector.shape}, dtype={vector.dtype}")
    return vector
