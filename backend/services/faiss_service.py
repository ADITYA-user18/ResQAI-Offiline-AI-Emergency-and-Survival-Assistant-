"""
services/faiss_service.py — FAISS Index Loader Service
=======================================================
Loads the pre-built FAISS index and metadata.json once at startup.
Provides semantic vector search over the emergency knowledge base.

IMPORTANT: This service NEVER rebuilds or modifies the FAISS index.
It loads existing files from knowledge/embeddings/ in read-only mode.
"""

import json
import numpy as np
from pathlib import Path
from typing import List, Tuple, Dict, Any, Optional

try:
    import faiss
except ImportError:
    raise ImportError(
        "faiss-cpu is not installed. Run: pip install faiss-cpu"
    )

try:
    from config import FAISS_INDEX_PATH, METADATA_JSON_PATH, TOP_K_RESULTS
    from utils.logger import get_logger
except ImportError:
    FAISS_INDEX_PATH   = Path("../knowledge/embeddings/faiss.index")
    METADATA_JSON_PATH = Path("../knowledge/embeddings/metadata.json")
    TOP_K_RESULTS      = 5
    import logging
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger(__name__)


class FAISSService:
    """
    Singleton-style service for loading and querying the FAISS vector index.

    The index was built using nomic-embed-text (768-dimensional vectors).
    Each vector corresponds to one entry in metadata.json via its vector_id.

    Search flow:
        1. Caller provides a query embedding (numpy float32 array).
        2. FAISS performs ANN (approximate nearest neighbor) search.
        3. Returns top-K (index positions, distances).
        4. Index positions map to metadata entries via vector_id.
    """

    def __init__(self) -> None:
        self._index: Optional[faiss.Index] = None
        self._metadata: List[Dict[str, Any]] = []
        self._loaded: bool = False

    # ─────────────────────────────────────────────────────────────────────────
    # LOADING
    # ─────────────────────────────────────────────────────────────────────────

    def load(self) -> None:
        """
        Load the FAISS index and metadata from disk.
        Call this once during application startup.

        Raises:
            FileNotFoundError: If either file is missing.
            RuntimeError:      If FAISS fails to read the index.
        """
        self._load_faiss_index()
        self._load_metadata()
        self._loaded = True
        logger.info(
            f"FAISS service ready — {self._index.ntotal} vectors, "
            f"{len(self._metadata)} metadata entries"
        )

    def _load_faiss_index(self) -> None:
        if not FAISS_INDEX_PATH.exists():
            raise FileNotFoundError(
                f"FAISS index not found at: {FAISS_INDEX_PATH}\n"
                "Run the embedding pipeline first to generate it."
            )
        try:
            self._index = faiss.read_index(str(FAISS_INDEX_PATH))
            logger.info(
                f"Loaded FAISS index: {FAISS_INDEX_PATH} "
                f"(d={self._index.d}, ntotal={self._index.ntotal})"
            )
        except Exception as e:
            raise RuntimeError(f"Failed to load FAISS index: {e}") from e

    def _load_metadata(self) -> None:
        if not METADATA_JSON_PATH.exists():
            raise FileNotFoundError(
                f"Metadata file not found at: {METADATA_JSON_PATH}"
            )
        try:
            with open(METADATA_JSON_PATH, "r", encoding="utf-8") as f:
                self._metadata = json.load(f)
            logger.info(f"Loaded metadata: {len(self._metadata)} entries")
        except json.JSONDecodeError as e:
            raise RuntimeError(f"Invalid JSON in metadata file: {e}") from e

    # ─────────────────────────────────────────────────────────────────────────
    # SEARCH
    # ─────────────────────────────────────────────────────────────────────────

    def search(
        self,
        query_vector: np.ndarray,
        top_k: int = TOP_K_RESULTS,
    ) -> List[Tuple[Dict[str, Any], float]]:
        """
        Search the FAISS index for the top-K nearest neighbors.

        Args:
            query_vector: 1D float32 numpy array (must match index dimension).
            top_k:        Number of results to return.

        Returns:
            List of (metadata_dict, distance) tuples, ordered by relevance.

        Raises:
            RuntimeError: If the service has not been loaded.
        """
        if not self._loaded:
            raise RuntimeError("FAISSService not loaded. Call load() first.")

        # Reshape to 2D (1, d) as FAISS expects a batch
        vec = query_vector.astype(np.float32).reshape(1, -1)

        # Normalize if using inner-product index (L2 index doesn't need this)
        # faiss.normalize_L2(vec)  # ← uncomment if index uses IP metric

        distances, indices = self._index.search(vec, top_k)

        results = []
        for dist, idx in zip(distances[0], indices[0]):
            if idx == -1:
                # FAISS returns -1 when fewer vectors than top_k exist
                continue
            meta = self._get_metadata_by_vector_id(int(idx))
            if meta:
                results.append((meta, float(dist)))

        logger.debug(f"FAISS search returned {len(results)} results")
        return results

    def _get_metadata_by_vector_id(self, vector_id: int) -> Optional[Dict[str, Any]]:
        """
        Look up metadata by vector_id (the FAISS index position).

        The metadata list is ordered by vector_id, so direct index access
        works when vector_ids are sequential starting from 0.
        Falls back to linear scan if not found at expected position.
        """
        # Fast path: direct index access (works for sequential vector_ids)
        if 0 <= vector_id < len(self._metadata):
            entry = self._metadata[vector_id]
            if entry.get("vector_id") == vector_id:
                return entry

        # Slow path: linear scan (handles gaps or reordering)
        for entry in self._metadata:
            if entry.get("vector_id") == vector_id:
                return entry

        logger.warning(f"No metadata found for vector_id={vector_id}")
        return None

    # ─────────────────────────────────────────────────────────────────────────
    # PROPERTIES
    # ─────────────────────────────────────────────────────────────────────────

    @property
    def is_loaded(self) -> bool:
        return self._loaded

    @property
    def vector_count(self) -> int:
        return self._index.ntotal if self._index else 0

    @property
    def metadata_count(self) -> int:
        return len(self._metadata)

    @property
    def dimension(self) -> int:
        return self._index.d if self._index else 0


# ── Module-level singleton ────────────────────────────────────────────────────
faiss_service = FAISSService()
