"""
services/knowledge_service.py — Processed Knowledge Loader
===========================================================
Loads the processed JSON knowledge files (firstaid, survival, legal)
and provides text lookup by chunk ID.

This service bridges the gap between FAISS metadata (which contains IDs
and titles) and the actual full text content stored in processed JSONs.

Flow:
    FAISS returns → metadata with 'id' field
    KnowledgeService.get_text(id) → full instructional text
"""

import json
from pathlib import Path
from typing import Dict, Optional, List

try:
    from config import FIRSTAID_JSON_PATH, SURVIVAL_JSON_PATH, LEGAL_JSON_PATH
    from utils.logger import get_logger
except ImportError:
    FIRSTAID_JSON_PATH = Path("../knowledge/processed/firstaid.json")
    SURVIVAL_JSON_PATH = Path("../knowledge/processed/survival.json")
    LEGAL_JSON_PATH    = Path("../knowledge/processed/legal.json")
    import logging
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger(__name__)


class KnowledgeService:
    """
    In-memory lookup table mapping chunk IDs to their full text.

    On startup, loads all three processed JSON files and indexes
    every entry by its 'id' field for O(1) text retrieval.
    """

    def __init__(self) -> None:
        # id → full chunk dict (includes 'text', 'title', 'category', etc.)
        self._knowledge_map: Dict[str, Dict] = {}
        self._loaded: bool = False

    # ─────────────────────────────────────────────────────────────────────────
    # LOADING
    # ─────────────────────────────────────────────────────────────────────────

    def load(self) -> None:
        """
        Load all processed knowledge JSON files into memory.
        Call once during application startup.
        """
        knowledge_files = [
            ("firstaid", FIRSTAID_JSON_PATH),
            ("survival",  SURVIVAL_JSON_PATH),
            ("legal",     LEGAL_JSON_PATH),
        ]

        total_loaded = 0
        for category, path in knowledge_files:
            count = self._load_file(category, path)
            total_loaded += count

        self._loaded = True
        logger.info(
            f"KnowledgeService ready — {total_loaded} chunks loaded "
            f"from {len(knowledge_files)} files"
        )

    def _load_file(self, category: str, path: Path) -> int:
        """Load a single processed JSON file. Returns number of entries loaded."""
        if not path.exists():
            logger.warning(f"Knowledge file not found (skipping): {path}")
            return 0

        try:
            with open(path, "r", encoding="utf-8") as f:
                entries = json.load(f)

            count = 0
            for entry in entries:
                chunk_id = entry.get("id")
                if chunk_id:
                    self._knowledge_map[chunk_id] = entry
                    count += 1
                else:
                    logger.warning(
                        f"Entry without 'id' in {path.name}: {entry.get('title', 'N/A')}"
                    )

            logger.info(f"Loaded {count} chunks from {path.name}")
            return count

        except json.JSONDecodeError as e:
            logger.error(f"JSON parse error in {path}: {e}")
            return 0
        except Exception as e:
            logger.error(f"Failed to load {path}: {e}")
            return 0

    # ─────────────────────────────────────────────────────────────────────────
    # RETRIEVAL
    # ─────────────────────────────────────────────────────────────────────────

    def get_text(self, chunk_id: str) -> Optional[str]:
        """
        Return the full text content for a given chunk ID.

        Args:
            chunk_id: The 'id' field from the processed JSON (e.g., "FA014-1").

        Returns:
            The full instructional text, or None if not found.
        """
        entry = self._knowledge_map.get(chunk_id)
        if entry:
            return entry.get("text", "")
        logger.warning(f"Chunk not found in knowledge map: {chunk_id}")
        return None

    def get_entry(self, chunk_id: str) -> Optional[Dict]:
        """Return the full entry dict for a chunk ID."""
        return self._knowledge_map.get(chunk_id)

    def get_all_ids(self) -> List[str]:
        """Return all loaded chunk IDs."""
        return list(self._knowledge_map.keys())

    @property
    def is_loaded(self) -> bool:
        return self._loaded

    @property
    def chunk_count(self) -> int:
        return len(self._knowledge_map)


# ── Module-level singleton ────────────────────────────────────────────────────
knowledge_service = KnowledgeService()
