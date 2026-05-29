"""
services/ollama_service.py — Ollama Local LLM Integration
==========================================================
Handles all communication with the local Ollama API server.
Supports model switching via config.py (LOW / MEDIUM / HIGH device tiers).

Endpoint used: POST http://localhost:11434/api/generate
"""

import json
import requests
from typing import Optional

try:
    from config import (
        OLLAMA_GENERATE_URL,
        OLLAMA_TAGS_URL,
        OLLAMA_MODEL,
        OLLAMA_TIMEOUT_SEC,
        OLLAMA_STREAM,
    )
    from utils.logger import get_logger
except ImportError:
    OLLAMA_GENERATE_URL = "http://localhost:11434/api/generate"
    OLLAMA_TAGS_URL     = "http://localhost:11434/api/tags"
    OLLAMA_MODEL        = "phi3:mini"
    OLLAMA_TIMEOUT_SEC  = 120
    OLLAMA_STREAM       = False
    import logging
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger(__name__)


class OllamaService:
    """
    Service for sending prompts to Ollama and receiving generated responses.

    Service for sending prompts to Ollama and receiving generated responses.
    Uses a single lightweight model for fast offline RAG.
    """

    def __init__(self, model: str = OLLAMA_MODEL) -> None:
        self.model   = model
        self.base_url = OLLAMA_GENERATE_URL
        logger.info(
            f"OllamaService initialized — model: {self.model}"
        )

    # ─────────────────────────────────────────────────────────────────────────
    # HEALTH CHECK
    # ─────────────────────────────────────────────────────────────────────────

    def is_available(self) -> bool:
        """
        Check if the Ollama server is reachable and the selected model is loaded.

        Returns:
            True if Ollama is up and the model is accessible.
        """
        try:
            response = requests.get(OLLAMA_TAGS_URL, timeout=5)
            if response.status_code != 200:
                return False
            data = response.json()
            loaded_models = [m.get("name", "") for m in data.get("models", [])]
            # Check for exact match or base name match (e.g., "phi3:mini" in "phi3:mini")
            for loaded in loaded_models:
                if self.model in loaded or loaded in self.model:
                    return True
            logger.warning(
                f"Ollama is running but model '{self.model}' is not pulled. "
                f"Available: {loaded_models}"
            )
            return False
        except requests.exceptions.ConnectionError:
            logger.warning("Ollama server is not reachable at localhost:11434")
            return False
        except Exception as e:
            logger.error(f"Ollama health check failed: {e}")
            return False

    def list_available_models(self) -> list:
        """Return list of model names currently available in Ollama."""
        try:
            response = requests.get(OLLAMA_TAGS_URL, timeout=5)
            data = response.json()
            return [m.get("name", "") for m in data.get("models", [])]
        except Exception:
            return []

    # ─────────────────────────────────────────────────────────────────────────
    # GENERATION
    # ─────────────────────────────────────────────────────────────────────────

    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """
        Send a prompt to Ollama and return the generated text.

        Args:
            prompt:        The full formatted prompt (context + question).
            system_prompt: Optional system-level instructions for the model.

        Returns:
            The model's response as a plain string.

        Raises:
            ConnectionError: If Ollama is not reachable.
            RuntimeError:    If the API returns an error status.
        """
        payload = {
            "model":  self.model,
            "prompt": prompt,
            "stream": OLLAMA_STREAM,
            "options": {
                "temperature": 0.3,      # Lower = more deterministic (safer for emergencies)
                "top_p":       0.9,
                "num_predict": 512,      # Max tokens in response
                "stop": ["###", "---"],  # Stop tokens to prevent runaway generation
            },
        }

        if system_prompt:
            payload["system"] = system_prompt

        logger.debug(f"Sending prompt to Ollama (model={self.model}, chars={len(prompt)})")

        try:
            response = requests.post(
                self.base_url,
                json=payload,
                timeout=OLLAMA_TIMEOUT_SEC,
            )
            response.raise_for_status()
        except requests.exceptions.ConnectionError:
            raise ConnectionError(
                "Cannot connect to Ollama. "
                "Make sure Ollama is running: `ollama serve`"
            )
        except requests.exceptions.Timeout:
            raise TimeoutError(
                f"Ollama did not respond within {OLLAMA_TIMEOUT_SEC} seconds. "
                "Try a smaller/faster model."
            )
        except requests.exceptions.HTTPError as e:
            raise RuntimeError(f"Ollama API error: {e}") from e

        try:
            data = response.json()
        except json.JSONDecodeError as e:
            raise RuntimeError(f"Invalid JSON from Ollama: {e}") from e

        answer = data.get("response", "").strip()

        if not answer:
            logger.warning("Ollama returned an empty response")
            return "I was unable to generate a response. Please try rephrasing your question."

        logger.debug(f"Ollama response received ({len(answer)} chars)")
        return answer

    def generate_stream(self, prompt: str, system_prompt: Optional[str] = None):
        """
        Send a prompt to Ollama and yield the generated text chunks as they arrive.
        """
        payload = {
            "model":  self.model,
            "prompt": prompt,
            "stream": True,
            "options": {
                "temperature": 0.3,
                "top_p":       0.9,
                "num_predict": 512,
                "stop": ["###", "---"],
            },
        }

        if system_prompt:
            payload["system"] = system_prompt

        try:
            response = requests.post(
                self.base_url,
                json=payload,
                timeout=OLLAMA_TIMEOUT_SEC,
                stream=True,
            )
            response.raise_for_status()

            for line in response.iter_lines():
                if line:
                    chunk = json.loads(line)
                    if "response" in chunk:
                        yield chunk["response"]

        except Exception as e:
            logger.error(f"Ollama stream error: {e}")
            yield f"\n[Error: AI generation failed - {str(e)}]"

    # ─────────────────────────────────────────────────────────────────────────
    # MODEL SWITCHING
    # ─────────────────────────────────────────────────────────────────────────

    def switch_model(self, model_name: str) -> None:
        """Switch to a different model at runtime."""
        old_model   = self.model
        self.model  = model_name
        logger.info(f"Model switched: {old_model} → {self.model}")


# ── Module-level singleton ────────────────────────────────────────────────────
ollama_service = OllamaService()
