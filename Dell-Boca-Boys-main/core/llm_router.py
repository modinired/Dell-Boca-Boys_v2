"""
Dual‑model language model router for Dell Bocca Boys.

This module provides a single entry point for generating responses using
both a local language model (served via Ollama) and an external provider
(e.g. Gemini).  It reads configuration from environment variables so that
models and API keys can be changed without modifying the code.  When both
models are available, it returns a dictionary containing each model’s
response.  Calling code can then apply its own selection or merging logic.

Environment variables
=====================

The following variables control the router:

- ``OLLAMA_BASE_URL`` (default ``http://localhost:11434``): the base URL of
  the running Ollama server hosting the local model.
- ``LOCAL_MODEL_NAME`` (default ``qwen2.5-coder:latest``): the name of the
  local model to load.  This should match a model tag returned by
  ``/api/tags`` on the Ollama server.
- ``GEMINI_API_KEY`` (empty by default): API key for the Gemini service.  If
  this is blank the router will not attempt to call Gemini.
- ``GEMINI_MODEL`` (default ``gemini-1.5-pro-latest``): the identifier of
  the Gemini model to use.

Example
-------

```
from core.llm_router import DualModelRouter

router = DualModelRouter()
results = router.query("Explain the n8n workflow generation pipeline.")
if "local" in results:
    print("Local model responded:\n", results["local"])
if "gemini" in results:
    print("Gemini responded:\n", results["gemini"])
```

Note that this module deliberately avoids raising exceptions for
connection errors.  Instead, any error encountered while querying a
provider will be returned as ``<provider>_error`` in the result dict.
This design allows callers to handle partial failures gracefully.
"""

from __future__ import annotations

import os
import requests
from typing import Dict, Any

# Conditional import: Gemini is optional.  If not available or no key
# configured, the router will simply skip Gemini calls.
try:
    import google.generativeai as genai  # type: ignore
    _HAS_GEMINI = True
except Exception:
    genai = None  # type: ignore
    _HAS_GEMINI = False


class DualModelRouter:
    """Route queries to local and remote language models.

    Instances of this class can be reused across many requests.  On
    initialisation it checks whether a local Ollama server is reachable,
    but does not attempt to connect to Gemini until a query is made.
    """

    def __init__(self) -> None:
        self.ollama_base = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434").rstrip("/")
        self.local_model = os.getenv("LOCAL_MODEL_NAME", "qwen2.5-coder:latest")
        self.gemini_api_key = os.getenv("GEMINI_API_KEY", "")
        self.gemini_model = os.getenv("GEMINI_MODEL", "gemini-1.5-pro-latest")
        self._ollama_available = self._check_ollama()
        self._configure_gemini()

    def _check_ollama(self) -> bool:
        """Return True if a local Ollama server is reachable."""
        try:
            resp = requests.get(f"{self.ollama_base}/api/tags", timeout=3)
            return resp.status_code == 200
        except Exception:
            return False

    def _configure_gemini(self) -> None:
        """Initialise Gemini if a key is provided and the SDK is available."""
        if self.gemini_api_key and _HAS_GEMINI:
            # Avoid re‑configuring on every query
            genai.configure(api_key=self.gemini_api_key)

    def _call_local(self, prompt: str) -> str:
        """Generate a response using the local model via Ollama.

        Raises requests.exceptions.RequestException if the request fails.
        """
        data = {
            "model": self.local_model,
            "prompt": prompt,
            "stream": False,
        }
        resp = requests.post(f"{self.ollama_base}/api/generate", json=data, timeout=60)
        resp.raise_for_status()
        body = resp.json()
        return body.get("response", "")

    def _call_gemini(self, prompt: str) -> str:
        """Generate a response using the Gemini service.

        Raises an exception if the SDK is unavailable or misconfigured.
        """
        if not self.gemini_api_key or not _HAS_GEMINI:
            raise RuntimeError("Gemini is not configured or the SDK is missing")
        model = genai.GenerativeModel(self.gemini_model)
        result = model.generate_content(prompt)
        return result.text  # type: ignore[no-any-return]

    def query(self, prompt: str) -> Dict[str, Any]:
        """Query both local and remote models and return their responses.

        :param prompt: The user input to send to the models.
        :returns: A dictionary whose keys are ``local``/``gemini`` for
          successful responses and ``local_error``/``gemini_error`` for
          encountered exceptions.
        """
        results: Dict[str, Any] = {}
        # Query local model if available
        if self._ollama_available:
            try:
                results["local"] = self._call_local(prompt)
            except Exception as exc:
                results["local_error"] = str(exc)
        # Query Gemini if configured
        if self.gemini_api_key and _HAS_GEMINI:
            try:
                results["gemini"] = self._call_gemini(prompt)
            except Exception as exc:
                results["gemini_error"] = str(exc)
        return results


__all__ = ["DualModelRouter"]