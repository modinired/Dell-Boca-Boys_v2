"""
Vito - Local Offline AI Coding Agent
Powered by Qwen 2.5 Coder

A lightweight, comprehensive code assistant that runs 100% locally.
Built by the Dell Boca Boys.
"""

__version__ = "1.0.0"
__author__ = "Dell Boca Boys - Vito Italian (Diet Bocca)"

from .code_agent import VitoAgent
from .llm_local import LocalLLM
from .memory import MemorySystem
from .config import Config

__all__ = ["VitoAgent", "LocalLLM", "MemorySystem", "Config"]
