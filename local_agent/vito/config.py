"""
Configuration management for Vito agent
"""

import os
from pathlib import Path
from typing import Optional
from dataclasses import dataclass
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


@dataclass
class Config:
    """Configuration for Vito agent"""

    # Qwen LLM settings
    qwen_endpoint: str
    qwen_model: str
    temperature: float
    max_tokens: int
    timeout: int

    # Memory settings
    memory_db_path: Path
    max_context_length: int
    enable_memory: bool

    # Agent settings
    agent_name: str
    log_level: str
    streaming: bool

    # API settings
    api_host: str
    api_port: int

    @classmethod
    def from_env(cls) -> "Config":
        """Create config from environment variables"""

        # Determine home directory for Vito data
        vito_home = Path(os.getenv("VITO_HOME", Path.home() / ".vito"))
        vito_home.mkdir(parents=True, exist_ok=True)

        return cls(
            # Qwen settings
            qwen_endpoint=os.getenv("QWEN_ENDPOINT", "http://localhost:8000/v1"),
            qwen_model=os.getenv("QWEN_MODEL", "Qwen/Qwen2.5-Coder-32B-Instruct"),
            temperature=float(os.getenv("TEMPERATURE", "0.1")),
            max_tokens=int(os.getenv("MAX_TOKENS", "4096")),
            timeout=int(os.getenv("LLM_TIMEOUT", "120")),

            # Memory settings
            memory_db_path=Path(os.getenv("MEMORY_DB_PATH", vito_home / "memory.db")),
            max_context_length=int(os.getenv("MAX_CONTEXT_LENGTH", "8000")),
            enable_memory=os.getenv("ENABLE_MEMORY", "true").lower() == "true",

            # Agent settings
            agent_name=os.getenv("AGENT_NAME", "Vito"),
            log_level=os.getenv("LOG_LEVEL", "INFO"),
            streaming=os.getenv("STREAMING", "true").lower() == "true",

            # API settings
            api_host=os.getenv("API_HOST", "0.0.0.0"),
            api_port=int(os.getenv("API_PORT", "8080")),
        )

    def __repr__(self) -> str:
        """String representation"""
        return (
            f"Config(\n"
            f"  Qwen: {self.qwen_endpoint} ({self.qwen_model})\n"
            f"  Memory: {self.memory_db_path}\n"
            f"  Agent: {self.agent_name}\n"
            f")"
        )


# Global config instance
_config: Optional[Config] = None


def get_config() -> Config:
    """Get global config instance"""
    global _config
    if _config is None:
        _config = Config.from_env()
    return _config


def reset_config():
    """Reset config (for testing)"""
    global _config
    _config = None
