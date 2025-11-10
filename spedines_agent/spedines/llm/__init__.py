"""
Spedines LLM Integration Module
Hybrid Gemini + Local Qwen with Draft-and-Polish Collaboration
"""

from .local import LocalQwenClient
from .gemini import GeminiClient
from .router import LLMRouter, RoutingStrategy
from .prompts import SpedinesPrompts, PromptTemplate

__all__ = [
    "LocalQwenClient",
    "GeminiClient",
    "LLMRouter",
    "RoutingStrategy",
    "SpedinesPrompts",
    "PromptTemplate",
]
