"""
Spedines Agent - Little Jim Spedines
Hybrid AI Agent with Continual Learning

A comprehensive AI assistant combining local Qwen 2.5 Coder with Google Gemini
for world-class reasoning, persistent memory, and autonomous task execution.
"""

__version__ = "1.0.0"
__author__ = "Dell Boca Boys - Little Jim Spedines"

from .agent import SpedinesAgent
from .config import SpedinesConfig

__all__ = ["SpedinesAgent", "SpedinesConfig"]
