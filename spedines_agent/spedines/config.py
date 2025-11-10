"""
Configuration management for Spedines Agent
"""

import os
from pathlib import Path
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field, validator
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class LLMConfig(BaseModel):
    """LLM Configuration"""
    # Gemini
    gemini_api_key: str = Field(..., description="Google Gemini API key")
    gemini_model: str = Field(default="gemini-2.0-flash-exp")
    gemini_max_tokens: int = Field(default=8192)
    gemini_temperature: float = Field(default=0.7)

    # Local Qwen
    qwen_endpoint: str = Field(default="http://localhost:11434/v1")
    qwen_model: str = Field(default="qwen2.5-coder:32b")
    qwen_max_tokens: int = Field(default=4096)
    qwen_temperature: float = Field(default=0.1)

    # Routing
    routing_strategy: str = Field(default="draft_polish")
    gemini_complexity_threshold: float = Field(default=0.6)


class GoogleConfig(BaseModel):
    """Google Cloud Configuration"""
    credentials_path: Path = Field(..., description="Service account JSON path")
    project_id: Optional[str] = None
    sheet_id: str = Field(..., description="Audit log Sheet ID")
    sheet_name: str = Field(default="SpedinesAuditLog")
    drive_folder_id: Optional[str] = None
    drive_watch_interval: int = Field(default=3600)  # 1 hour

    @validator("credentials_path")
    def validate_credentials_path(cls, v):
        if not Path(v).exists():
            raise ValueError(f"Credentials file not found: {v}")
        return v


class MemoryConfig(BaseModel):
    """Memory System Configuration"""
    chroma_db_path: Path = Field(default=Path("./data/chromadb"))
    chroma_collection_name: str = Field(default="spedines_memory")
    enable_memory: bool = Field(default=True)

    # Embeddings
    embedding_provider: str = Field(default="sentence-transformers")
    embedding_model: str = Field(default="all-MiniLM-L6-v2")
    embedding_dimension: int = Field(default=384)

    # Retention
    max_memory_entries: int = Field(default=100000)
    memory_cleanup_days: int = Field(default=90)

    # RAG
    rag_top_k: int = Field(default=5)
    rag_min_similarity: float = Field(default=0.7)


class IngestConfig(BaseModel):
    """Data Ingestion Configuration"""
    # Financial
    enable_financial_data: bool = Field(default=True)
    financial_api_key: Optional[str] = None
    financial_symbols: str = Field(default="AAPL,GOOGL,MSFT,AMZN")
    financial_pull_interval: int = Field(default=86400)  # Daily

    # Scholarly
    enable_scholarly_data: bool = Field(default=True)
    arxiv_categories: str = Field(default="cs.AI,cs.CL,cs.LG")
    arxiv_max_results: int = Field(default=10)
    scholarly_pull_interval: int = Field(default=86400)  # Daily

    # RSS
    rss_feeds: Optional[str] = None


class ActivityConfig(BaseModel):
    """Activity Tracking Configuration"""
    enable_activity_tracking: bool = Field(default=False)
    activity_consent_given: bool = Field(default=False)
    activity_consent_date: Optional[str] = None

    # What to track
    track_app_usage: bool = Field(default=True)
    track_window_titles: bool = Field(default=True)
    track_active_time: bool = Field(default=True)
    track_screenshots: bool = Field(default=False)

    # Storage
    activity_log_path: Path = Field(default=Path("./data/activity_logs"))
    activity_log_encryption: bool = Field(default=True)
    activity_log_retention_days: int = Field(default=30)


class ReflectionConfig(BaseModel):
    """Reflection & Learning Configuration"""
    daily_reflection_enabled: bool = Field(default=True)
    daily_reflection_time: str = Field(default="20:00")
    reflection_summary_length: str = Field(default="comprehensive")

    # Training data
    auto_collect_training_data: bool = Field(default=True)
    training_data_quality_threshold: int = Field(default=4)  # 1-5 scale
    training_data_path: Path = Field(default=Path("./data/training"))

    # Fine-tuning
    enable_auto_finetuning: bool = Field(default=False)
    finetuning_interval_days: int = Field(default=7)
    finetuning_method: str = Field(default="lora")
    finetuning_learning_rate: float = Field(default=0.0001)


class SandboxConfig(BaseModel):
    """Sandbox Execution Configuration"""
    sandbox_enabled: bool = Field(default=True)
    sandbox_type: str = Field(default="subprocess")  # subprocess or docker
    sandbox_timeout: int = Field(default=30)  # seconds
    sandbox_max_memory_mb: int = Field(default=512)
    sandbox_network_allowed: bool = Field(default=False)

    # Docker
    sandbox_docker_image: str = Field(default="python:3.11-slim")
    sandbox_docker_network: str = Field(default="none")


class APIConfig(BaseModel):
    """API Server Configuration"""
    api_host: str = Field(default="0.0.0.0")
    api_port: int = Field(default=8080)
    api_workers: int = Field(default=1)
    api_reload: bool = Field(default=False)

    # Security
    api_key_required: bool = Field(default=False)
    api_key: Optional[str] = None
    cors_origins: str = Field(default="http://localhost:3000,http://localhost:8080")

    # Rate limiting
    rate_limit_enabled: bool = Field(default=True)
    rate_limit_requests: int = Field(default=60)
    rate_limit_period: int = Field(default=60)


class PersonaConfig(BaseModel):
    """Agent Persona Configuration"""
    agent_name: str = Field(default="Little Jim Spedines")
    agent_nickname: str = Field(default="Spedines")
    agent_role: str = Field(default="Hybrid AI Assistant")
    personality_style: str = Field(default="professional_playful")
    verbosity: str = Field(default="medium")
    emoji_usage: str = Field(default="minimal")


class MonitoringConfig(BaseModel):
    """Logging & Monitoring Configuration"""
    log_level: str = Field(default="INFO")
    log_path: Path = Field(default=Path("./logs"))
    log_max_size_mb: int = Field(default=100)
    log_backup_count: int = Field(default=5)

    # Metrics
    enable_metrics: bool = Field(default=True)
    metrics_port: int = Field(default=9090)
    enable_telemetry: bool = Field(default=False)


class SpedinesConfig(BaseSettings):
    """
    Main Spedines Configuration

    Loads configuration from environment variables and .env file
    """

    # Component configs
    llm: LLMConfig
    google: GoogleConfig
    memory: MemoryConfig
    ingest: IngestConfig
    activity: ActivityConfig
    reflection: ReflectionConfig
    sandbox: SandboxConfig
    api: APIConfig
    persona: PersonaConfig
    monitoring: MonitoringConfig

    # Advanced settings
    enable_cache: bool = Field(default=True)
    cache_ttl_seconds: int = Field(default=3600)
    cache_path: Path = Field(default=Path("./data/cache"))

    database_url: str = Field(default="sqlite:///./data/spedines.db")

    # Backup
    auto_backup_enabled: bool = Field(default=True)
    backup_path: Path = Field(default=Path("./data/backups"))
    backup_interval_days: int = Field(default=7)
    backup_retention_days: int = Field(default=30)

    # Development
    debug_mode: bool = Field(default=False)
    profile_performance: bool = Field(default=False)
    mock_external_apis: bool = Field(default=False)

    # Cost tracking
    gemini_monthly_budget_usd: float = Field(default=100.0)
    gemini_cost_per_1k_input: float = Field(default=0.00025)
    gemini_cost_per_1k_output: float = Field(default=0.0005)
    alert_threshold_percent: int = Field(default=80)

    track_token_usage: bool = Field(default=True)
    track_api_costs: bool = Field(default=True)
    cost_log_path: Path = Field(default=Path("./data/costs"))

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        env_nested_delimiter = "__"
        case_sensitive = False

    @classmethod
    def from_env(cls) -> "SpedinesConfig":
        """Create config from environment variables"""
        return cls(
            llm=LLMConfig(
                gemini_api_key=os.getenv("GEMINI_API_KEY", ""),
                gemini_model=os.getenv("GEMINI_MODEL", "gemini-2.0-flash-exp"),
                gemini_max_tokens=int(os.getenv("GEMINI_MAX_TOKENS", "8192")),
                gemini_temperature=float(os.getenv("GEMINI_TEMPERATURE", "0.7")),
                qwen_endpoint=os.getenv("QWEN_ENDPOINT", "http://localhost:11434/v1"),
                qwen_model=os.getenv("QWEN_MODEL", "qwen2.5-coder:32b"),
                qwen_max_tokens=int(os.getenv("QWEN_MAX_TOKENS", "4096")),
                qwen_temperature=float(os.getenv("QWEN_TEMPERATURE", "0.1")),
                routing_strategy=os.getenv("ROUTING_STRATEGY", "draft_polish"),
                gemini_complexity_threshold=float(os.getenv("GEMINI_COMPLEXITY_THRESHOLD", "0.6")),
            ),
            google=GoogleConfig(
                credentials_path=Path(os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "./config/service-account.json")),
                project_id=os.getenv("GOOGLE_PROJECT_ID"),
                sheet_id=os.getenv("GOOGLE_SHEET_ID", ""),
                sheet_name=os.getenv("GOOGLE_SHEET_NAME", "SpedinesAuditLog"),
                drive_folder_id=os.getenv("GOOGLE_DRIVE_FOLDER_ID"),
                drive_watch_interval=int(os.getenv("GOOGLE_DRIVE_WATCH_INTERVAL", "3600")),
            ),
            memory=MemoryConfig(
                chroma_db_path=Path(os.getenv("CHROMA_DB_PATH", "./data/chromadb")),
                chroma_collection_name=os.getenv("CHROMA_COLLECTION_NAME", "spedines_memory"),
                enable_memory=os.getenv("ENABLE_MEMORY", "true").lower() == "true",
                embedding_provider=os.getenv("EMBEDDING_PROVIDER", "sentence-transformers"),
                embedding_model=os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2"),
                embedding_dimension=int(os.getenv("EMBEDDING_DIMENSION", "384")),
                max_memory_entries=int(os.getenv("MAX_MEMORY_ENTRIES", "100000")),
                memory_cleanup_days=int(os.getenv("MEMORY_CLEANUP_DAYS", "90")),
                rag_top_k=int(os.getenv("RAG_TOP_K", "5")),
                rag_min_similarity=float(os.getenv("RAG_MIN_SIMILARITY", "0.7")),
            ),
            ingest=IngestConfig(
                enable_financial_data=os.getenv("ENABLE_FINANCIAL_DATA", "true").lower() == "true",
                financial_api_key=os.getenv("FINANCIAL_API_KEY"),
                financial_symbols=os.getenv("FINANCIAL_SYMBOLS", "AAPL,GOOGL,MSFT,AMZN"),
                financial_pull_interval=int(os.getenv("FINANCIAL_PULL_INTERVAL", "86400")),
                enable_scholarly_data=os.getenv("ENABLE_SCHOLARLY_DATA", "true").lower() == "true",
                arxiv_categories=os.getenv("ARXIV_CATEGORIES", "cs.AI,cs.CL,cs.LG"),
                arxiv_max_results=int(os.getenv("ARXIV_MAX_RESULTS", "10")),
                scholarly_pull_interval=int(os.getenv("SCHOLARLY_PULL_INTERVAL", "86400")),
                rss_feeds=os.getenv("RSS_FEEDS"),
            ),
            activity=ActivityConfig(
                enable_activity_tracking=os.getenv("ENABLE_ACTIVITY_TRACKING", "false").lower() == "true",
                activity_consent_given=os.getenv("ACTIVITY_CONSENT_GIVEN", "false").lower() == "true",
                activity_consent_date=os.getenv("ACTIVITY_CONSENT_DATE"),
                track_app_usage=os.getenv("TRACK_APP_USAGE", "true").lower() == "true",
                track_window_titles=os.getenv("TRACK_WINDOW_TITLES", "true").lower() == "true",
                track_active_time=os.getenv("TRACK_ACTIVE_TIME", "true").lower() == "true",
                track_screenshots=os.getenv("TRACK_SCREENSHOTS", "false").lower() == "true",
                activity_log_path=Path(os.getenv("ACTIVITY_LOG_PATH", "./data/activity_logs")),
                activity_log_encryption=os.getenv("ACTIVITY_LOG_ENCRYPTION", "true").lower() == "true",
                activity_log_retention_days=int(os.getenv("ACTIVITY_LOG_RETENTION_DAYS", "30")),
            ),
            reflection=ReflectionConfig(
                daily_reflection_enabled=os.getenv("DAILY_REFLECTION_ENABLED", "true").lower() == "true",
                daily_reflection_time=os.getenv("DAILY_REFLECTION_TIME", "20:00"),
                reflection_summary_length=os.getenv("REFLECTION_SUMMARY_LENGTH", "comprehensive"),
                auto_collect_training_data=os.getenv("AUTO_COLLECT_TRAINING_DATA", "true").lower() == "true",
                training_data_quality_threshold=int(os.getenv("TRAINING_DATA_QUALITY_THRESHOLD", "4")),
                training_data_path=Path(os.getenv("TRAINING_DATA_PATH", "./data/training")),
                enable_auto_finetuning=os.getenv("ENABLE_AUTO_FINETUNING", "false").lower() == "true",
                finetuning_interval_days=int(os.getenv("FINETUNING_INTERVAL_DAYS", "7")),
                finetuning_method=os.getenv("FINETUNING_METHOD", "lora"),
                finetuning_learning_rate=float(os.getenv("FINETUNING_LEARNING_RATE", "0.0001")),
            ),
            sandbox=SandboxConfig(
                sandbox_enabled=os.getenv("SANDBOX_ENABLED", "true").lower() == "true",
                sandbox_type=os.getenv("SANDBOX_TYPE", "subprocess"),
                sandbox_timeout=int(os.getenv("SANDBOX_TIMEOUT", "30")),
                sandbox_max_memory_mb=int(os.getenv("SANDBOX_MAX_MEMORY_MB", "512")),
                sandbox_network_allowed=os.getenv("SANDBOX_NETWORK_ALLOWED", "false").lower() == "true",
                sandbox_docker_image=os.getenv("SANDBOX_DOCKER_IMAGE", "python:3.11-slim"),
                sandbox_docker_network=os.getenv("SANDBOX_DOCKER_NETWORK", "none"),
            ),
            api=APIConfig(
                api_host=os.getenv("API_HOST", "0.0.0.0"),
                api_port=int(os.getenv("API_PORT", "8080")),
                api_workers=int(os.getenv("API_WORKERS", "1")),
                api_reload=os.getenv("API_RELOAD", "false").lower() == "true",
                api_key_required=os.getenv("API_KEY_REQUIRED", "false").lower() == "true",
                api_key=os.getenv("API_KEY"),
                cors_origins=os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:8080"),
                rate_limit_enabled=os.getenv("RATE_LIMIT_ENABLED", "true").lower() == "true",
                rate_limit_requests=int(os.getenv("RATE_LIMIT_REQUESTS", "60")),
                rate_limit_period=int(os.getenv("RATE_LIMIT_PERIOD", "60")),
            ),
            persona=PersonaConfig(
                agent_name=os.getenv("AGENT_NAME", "Little Jim Spedines"),
                agent_nickname=os.getenv("AGENT_NICKNAME", "Spedines"),
                agent_role=os.getenv("AGENT_ROLE", "Hybrid AI Assistant"),
                personality_style=os.getenv("PERSONALITY_STYLE", "professional_playful"),
                verbosity=os.getenv("VERBOSITY", "medium"),
                emoji_usage=os.getenv("EMOJI_USAGE", "minimal"),
            ),
            monitoring=MonitoringConfig(
                log_level=os.getenv("LOG_LEVEL", "INFO"),
                log_path=Path(os.getenv("LOG_PATH", "./logs")),
                log_max_size_mb=int(os.getenv("LOG_MAX_SIZE_MB", "100")),
                log_backup_count=int(os.getenv("LOG_BACKUP_COUNT", "5")),
                enable_metrics=os.getenv("ENABLE_METRICS", "true").lower() == "true",
                metrics_port=int(os.getenv("METRICS_PORT", "9090")),
                enable_telemetry=os.getenv("ENABLE_TELEMETRY", "false").lower() == "true",
            ),
        )

    def ensure_directories(self):
        """Create necessary directories"""
        dirs = [
            self.memory.chroma_db_path,
            self.activity.activity_log_path,
            self.reflection.training_data_path,
            self.cache_path,
            self.backup_path,
            self.monitoring.log_path,
            self.cost_log_path,
        ]

        for dir_path in dirs:
            dir_path.mkdir(parents=True, exist_ok=True)

    def __repr__(self) -> str:
        return f"SpedinesConfig(agent={self.persona.agent_name}, llm={self.llm.routing_strategy})"


# Global config instance
_config: Optional[SpedinesConfig] = None


def get_config() -> SpedinesConfig:
    """Get global config instance"""
    global _config
    if _config is None:
        _config = SpedinesConfig.from_env()
        _config.ensure_directories()
    return _config


def reset_config():
    """Reset config (for testing)"""
    global _config
    _config = None
