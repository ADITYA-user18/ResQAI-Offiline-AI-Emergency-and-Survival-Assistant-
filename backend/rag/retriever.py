"""
rag/retriever.py — Semantic Retrieval Engine
============================================
The core RAG retrieval pipeline. Combines embedding generation,
FAISS vector search, and knowledge text lookup into one callable.

Full pipeline:
    User Query
       ↓ embed_query()          — generate vector via nomic-embed-text
       ↓ faiss_service.search() — find top-K similar vectors
       ↓ knowledge_service.get_text(id) — fetch full chunk text
       ↓ return RetrievedChunks

Retrieved chunks are then passed to prompt_builder.py
to construct the final LLM prompt.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any

try:
    from rag.embeddings import embed_query
    from services.faiss_service import faiss_service
    from services.knowledge_service import knowledge_service
    from utils.logger import get_logger
    from config import TOP_K_RESULTS, MAX_CONTEXT_CHARS
except ImportError:
    import logging
    get_logger = lambda name: logging.getLogger(name)
    TOP_K_RESULTS    = 5
    MAX_CONTEXT_CHARS = 3000

logger = get_logger(__name__)


@dataclass
class RetrievedChunk:
    """A single knowledge chunk returned by the retrieval engine."""
    chunk_id:   str
    title:      str
    category:   str
    priority:   str
    source:     str
    text:       str
    distance:   float    # FAISS L2 distance (lower = more similar)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "chunk_id": self.chunk_id,
            "title":    self.title,
            "category": self.category,
            "priority": self.priority,
            "source":   self.source,
            "text":     self.text,
            "distance": round(self.distance, 4),
        }


def retrieve(query: str, top_k: int = TOP_K_RESULTS) -> List[RetrievedChunk]:
    """
    Full semantic retrieval pipeline for a user query.

    Steps:
        1. Embed the query using nomic-embed-text via Ollama.
        2. Search FAISS for top-K nearest vectors.
        3. Map each FAISS result (vector_id) to its metadata.
        4. Fetch full text from the knowledge service using the chunk ID.
        5. Return list of RetrievedChunk objects.

    Args:
        query: The user's natural-language question (already sanitized).
        top_k: Number of chunks to retrieve.

    Returns:
        List of RetrievedChunk objects, ordered by relevance.

    Raises:
        ConnectionError: If Ollama is unreachable for embedding.
        RuntimeError:    If FAISS service is not loaded.
    """
    if not faiss_service.is_loaded:
        raise RuntimeError(
            "FAISS service not loaded. Check server startup logs."
        )
    if not knowledge_service.is_loaded:
        raise RuntimeError(
            "Knowledge service not loaded. Check server startup logs."
        )

    logger.info(f"Retrieving context for query: '{query[:100]}'")

    # ── Step 1: Embed the user query ──────────────────────────────────────────
    query_vector = embed_query(query)
    logger.debug(f"Query embedded: shape={query_vector.shape}")

    # ── Step 2: FAISS search ──────────────────────────────────────────────────
    faiss_results = faiss_service.search(query_vector, top_k=top_k)
    logger.debug(f"FAISS returned {len(faiss_results)} raw results")

    # ── Step 3 & 4: Map to full chunks ────────────────────────────────────────
    chunks: List[RetrievedChunk] = []

    for metadata, distance in faiss_results:
        chunk_id = metadata.get("id")
        if not chunk_id:
            logger.warning(f"Metadata entry missing 'id' field: {metadata}")
            continue

        # Fetch full text from the processed knowledge store
        text = knowledge_service.get_text(chunk_id)
        if not text:
            logger.warning(
                f"No text found for chunk '{chunk_id}' — "
                "metadata exists in FAISS but not in processed JSONs"
            )
            # Fallback: use title as minimal context
            text = metadata.get("title", "No text available")

        chunk = RetrievedChunk(
            chunk_id = chunk_id,
            title    = metadata.get("title", "Unknown"),
            category = metadata.get("category", "unknown"),
            priority = metadata.get("priority", "unknown"),
            source   = metadata.get("source", "unknown"),
            text     = text,
            distance = distance,
        )
        chunks.append(chunk)

    # Sort by distance (ascending = most relevant first)
    chunks.sort(key=lambda c: c.distance)

    logger.info(
        f"Retrieved {len(chunks)} chunks "
        f"(categories: {list({c.category for c in chunks})})"
    )
    return chunks


def build_context_text(chunks: List[RetrievedChunk], max_chars: int = MAX_CONTEXT_CHARS) -> str:
    """
    Concatenate retrieved chunk texts into a single context block.
    Respects the max_chars budget to avoid overflowing the LLM context window.

    Args:
        chunks:    List of RetrievedChunk objects (ordered by relevance).
        max_chars: Maximum total characters for the combined context.

    Returns:
        A formatted context string ready for the prompt builder.
    """
    context_parts = []
    total_chars   = 0

    for i, chunk in enumerate(chunks, start=1):
        header = f"[{i}] {chunk.title} ({chunk.category.upper()}, Priority: {chunk.priority.upper()})"
        entry  = f"{header}\n{chunk.text}\n"

        if total_chars + len(entry) > max_chars:
            logger.debug(
                f"Context budget reached at chunk {i} — "
                f"stopping at {total_chars} chars"
            )
            break

        context_parts.append(entry)
        total_chars += len(entry)

    return "\n".join(context_parts).strip()
