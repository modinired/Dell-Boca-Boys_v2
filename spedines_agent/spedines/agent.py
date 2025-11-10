"""
Spedines Agent - Little Jim Spedines
Main agent class coordinating all components
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from dataclasses import dataclass, field
import asyncio

from .config import SpedinesConfig
from .llm.router import LLMRouter, RoutingStrategy, RoutingResult, create_router_from_config
from .llm.prompts import PromptTemplate
from .memory.chroma import ChromaMemoryStore, create_memory_store
from .memory.retrieval import MemoryRetriever, create_memory_retriever
from .google.sheets import GoogleSheetsLogger, create_sheets_logger
from .google.drive import GoogleDriveIngestor, create_drive_ingestor

logger = logging.getLogger(__name__)


@dataclass
class AgentResponse:
    """Response from Spedines agent"""
    response: str
    routing_result: RoutingResult
    memory_context: List[Dict[str, Any]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


class SpedinesAgent:
    """
    Little Jim Spedines - Main Agent Class

    Coordinates LLM, memory, Google integrations for intelligent assistance
    """

    def __init__(self, config: SpedinesConfig):
        """
        Initialize Spedines agent

        Args:
            config: SpedinesConfig with all settings
        """

        self.config = config

        logger.info("Initializing Little Jim Spedines agent...")

        # Initialize LLM router
        logger.info("Initializing LLM router...")
        self.llm_router = asyncio.run(create_router_from_config({
            "qwen_endpoint": config.llm.qwen_endpoint,
            "qwen_model": config.llm.qwen_model,
            "qwen_temperature": config.llm.qwen_temperature,
            "gemini_api_key": config.llm.gemini_api_key,
            "gemini_model": config.llm.gemini_model,
            "gemini_temperature": config.llm.gemini_temperature,
            "routing_strategy": config.llm.routing_strategy,
            "complexity_threshold": config.llm.gemini_complexity_threshold,
            "max_tokens": config.llm.max_tokens
        }))

        # Initialize memory system if enabled
        self.memory_store = None
        self.memory_retriever = None

        if config.memory.enable_memory:
            logger.info("Initializing memory system...")

            self.memory_store = create_memory_store(
                persist_directory=str(config.memory.chroma_db_path),
                collection_name=config.memory.collection_name,
                embedding_model=config.memory.embedding_model
            )

            self.memory_retriever = create_memory_retriever(
                memory_store=self.memory_store,
                strategy=config.memory.rag_strategy,
                top_k=config.memory.rag_top_k,
                min_similarity=config.memory.rag_min_similarity
            )

        # Initialize Google Sheets logger if enabled
        self.sheets_logger = None

        if config.google.enable_sheets_logging and config.google.sheet_id:
            logger.info("Initializing Google Sheets logger...")

            try:
                self.sheets_logger = create_sheets_logger(
                    spreadsheet_id=config.google.sheet_id,
                    credentials_path=str(config.google.credentials_path)
                )

            except Exception as e:
                logger.error(f"Failed to initialize Sheets logger: {e}")
                if config.google.require_sheets:
                    raise

        # Initialize Google Drive ingestor if enabled
        self.drive_ingestor = None

        if config.google.enable_drive_ingestion and config.google.drive_folder_id:
            logger.info("Initializing Google Drive ingestor...")

            try:
                self.drive_ingestor = create_drive_ingestor(
                    folder_id=config.google.drive_folder_id,
                    download_dir=str(config.ingest.drive_download_dir),
                    credentials_path=str(config.google.credentials_path),
                    poll_interval_minutes=config.ingest.drive_poll_interval_minutes
                )

            except Exception as e:
                logger.error(f"Failed to initialize Drive ingestor: {e}")

        # Metrics
        self.total_queries = 0
        self.successful_queries = 0
        self.failed_queries = 0

        logger.info("Spedines agent initialized successfully!")

    async def query(
        self,
        user_input: str,
        template: PromptTemplate = PromptTemplate.GENERAL_QUERY,
        routing_strategy: Optional[RoutingStrategy] = None,
        use_memory: bool = True,
        save_to_memory: bool = True,
        log_to_sheets: bool = True,
        **kwargs
    ) -> AgentResponse:
        """
        Process a user query

        Args:
            user_input: User's question/request
            template: Prompt template to use
            routing_strategy: Override default routing
            use_memory: Use memory context
            save_to_memory: Save interaction to memory
            log_to_sheets: Log to Google Sheets
            **kwargs: Additional parameters for LLM

        Returns:
            AgentResponse with the answer and metadata
        """

        self.total_queries += 1
        start_time = datetime.now()

        logger.info(f"Processing query: {user_input[:100]}...")

        try:
            # Retrieve relevant memory context
            memory_results = []
            if use_memory and self.memory_retriever:
                logger.debug("Retrieving memory context...")

                memory_results = self.memory_retriever.retrieve(
                    query=user_input,
                    strategy=None  # Use default from config
                )

                logger.info(f"Retrieved {len(memory_results)} relevant memories")

            # Convert memory results for LLM
            memory_context_for_llm = [
                {
                    "content": m.content,
                    "similarity": m.similarity,
                    "metadata": m.metadata
                }
                for m in memory_results
            ]

            # Route query through LLM
            routing_result = await self.llm_router.query(
                prompt=user_input,
                template=template,
                strategy=routing_strategy,
                memory_results=memory_context_for_llm,
                **kwargs
            )

            # Save to memory if enabled
            if save_to_memory and self.memory_store:
                logger.debug("Saving interaction to memory...")

                # Save user query
                self.memory_store.add_memory(
                    content=user_input,
                    metadata={
                        "source": "conversation",
                        "type": "user_query",
                        "timestamp": datetime.now().isoformat()
                    }
                )

                # Save assistant response
                self.memory_store.add_memory(
                    content=routing_result.response,
                    metadata={
                        "source": "conversation",
                        "type": "assistant_response",
                        "timestamp": datetime.now().isoformat(),
                        "llm_used": routing_result.strategy,
                        "template": template.value
                    }
                )

            # Log to Sheets if enabled
            if log_to_sheets and self.sheets_logger:
                logger.debug("Logging to Google Sheets...")

                try:
                    self.sheets_logger.log_interaction(
                        event_type="query",
                        user_query=user_input,
                        assistant_response=routing_result.response,
                        llm_used=routing_result.strategy,
                        tokens_used=routing_result.metrics.gemini_metrics.total_tokens if routing_result.metrics.gemini_used else routing_result.metrics.local_metrics.total_tokens if routing_result.metrics.local_used else 0,
                        latency_ms=routing_result.metrics.total_latency_ms,
                        cost_usd=routing_result.metrics.total_cost_usd,
                        success=routing_result.metrics.success,
                        metadata={
                            "template": template.value,
                            "memory_results": len(memory_results)
                        }
                    )

                except Exception as e:
                    logger.error(f"Failed to log to Sheets: {e}")

            self.successful_queries += 1

            # Create response
            end_time = datetime.now()
            total_time = (end_time - start_time).total_seconds() * 1000

            logger.info(
                f"Query completed successfully in {total_time:.0f}ms "
                f"(LLM: {routing_result.metrics.total_latency_ms:.0f}ms)"
            )

            return AgentResponse(
                response=routing_result.response,
                routing_result=routing_result,
                memory_context=memory_context_for_llm,
                metadata={
                    "total_latency_ms": total_time,
                    "template": template.value,
                    "memory_used": use_memory,
                    "memory_results_count": len(memory_results)
                }
            )

        except Exception as e:
            self.failed_queries += 1

            logger.error(f"Query failed: {e}", exc_info=True)

            # Log failure to Sheets
            if log_to_sheets and self.sheets_logger:
                try:
                    self.sheets_logger.log_interaction(
                        event_type="error",
                        user_query=user_input,
                        assistant_response=f"Error: {str(e)}",
                        llm_used="none",
                        success=False,
                        metadata={"error": str(e)}
                    )
                except Exception:
                    pass

            # Re-raise
            raise AgentError(f"Query failed: {e}") from e

    async def chat(
        self,
        user_input: str,
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> AgentResponse:
        """
        Chat interface with conversation history

        Args:
            user_input: User's message
            conversation_history: Optional conversation history

        Returns:
            AgentResponse
        """

        # For now, delegate to query
        # In future, could maintain conversation state
        return await self.query(
            user_input=user_input,
            template=PromptTemplate.GENERAL_QUERY
        )

    def add_knowledge(
        self,
        content: str,
        source: str = "manual",
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Add knowledge to memory

        Args:
            content: Knowledge content
            source: Source of knowledge
            tags: Optional tags
            metadata: Optional metadata

        Returns:
            Memory ID
        """

        if not self.memory_store:
            raise AgentError("Memory system not enabled")

        logger.info(f"Adding knowledge from {source}: {content[:100]}...")

        # Build metadata
        full_metadata = {
            "source": "learned",
            "learned_from": source,
            "timestamp": datetime.now().isoformat()
        }

        if tags:
            full_metadata["tags"] = tags

        if metadata:
            full_metadata.update(metadata)

        # Add to memory
        memory_id = self.memory_store.add_memory(
            content=content,
            metadata=full_metadata
        )

        logger.info(f"Added knowledge with ID: {memory_id}")

        return memory_id

    def search_memory(
        self,
        query: str,
        top_k: int = 5,
        source_filter: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Search memory for relevant information

        Args:
            query: Search query
            top_k: Number of results
            source_filter: Optional source filter

        Returns:
            List of memory results
        """

        if not self.memory_retriever:
            raise AgentError("Memory system not enabled")

        logger.info(f"Searching memory: {query[:100]}...")

        metadata_filter = {"source": source_filter} if source_filter else None

        results = self.memory_retriever.retrieve(
            query=query,
            top_k=top_k,
            metadata_filter=metadata_filter
        )

        return [
            {
                "content": r.content,
                "similarity": r.similarity,
                "metadata": r.metadata,
                "id": r.memory_id
            }
            for r in results
        ]

    def health_check(self) -> Dict[str, Any]:
        """
        Check health of all components

        Returns:
            Health status dictionary
        """

        logger.info("Running health check...")

        health = {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "components": {}
        }

        # Check LLM
        try:
            llm_health = self.llm_router.health_check()
            health["components"]["llm"] = llm_health

            if llm_health.get("overall_status") != "healthy":
                health["status"] = "degraded"

        except Exception as e:
            health["components"]["llm"] = {"status": "unhealthy", "error": str(e)}
            health["status"] = "degraded"

        # Check memory
        if self.memory_store:
            try:
                memory_count = self.memory_store.count()
                health["components"]["memory"] = {
                    "status": "healthy",
                    "total_memories": memory_count
                }

            except Exception as e:
                health["components"]["memory"] = {"status": "unhealthy", "error": str(e)}
                health["status"] = "degraded"

        # Check Sheets
        if self.sheets_logger:
            try:
                sheets_metrics = self.sheets_logger.get_metrics()
                health["components"]["sheets"] = {
                    "status": "healthy",
                    "metrics": sheets_metrics
                }

            except Exception as e:
                health["components"]["sheets"] = {"status": "unhealthy", "error": str(e)}

        # Check Drive
        if self.drive_ingestor:
            try:
                drive_metrics = self.drive_ingestor.get_metrics()
                health["components"]["drive"] = {
                    "status": "healthy",
                    "metrics": drive_metrics
                }

            except Exception as e:
                health["components"]["drive"] = {"status": "unhealthy", "error": str(e)}

        return health

    def get_metrics(self) -> Dict[str, Any]:
        """Get comprehensive agent metrics"""

        metrics = {
            "agent": {
                "total_queries": self.total_queries,
                "successful_queries": self.successful_queries,
                "failed_queries": self.failed_queries,
                "success_rate": self.successful_queries / max(self.total_queries, 1)
            }
        }

        # LLM metrics
        metrics["llm"] = self.llm_router.get_metrics()

        # Memory metrics
        if self.memory_store and self.memory_retriever:
            metrics["memory"] = {
                "store": self.memory_store.get_metrics(),
                "retriever": self.memory_retriever.get_metrics()
            }

        # Sheets metrics
        if self.sheets_logger:
            metrics["sheets"] = self.sheets_logger.get_metrics()

        # Drive metrics
        if self.drive_ingestor:
            metrics["drive"] = self.drive_ingestor.get_metrics()

        return metrics


class AgentError(Exception):
    """Custom exception for agent errors"""
    pass


# Factory function

def create_spedines_agent(
    config_path: Optional[str] = None,
    env_file: Optional[str] = None
) -> SpedinesAgent:
    """
    Create Spedines agent from configuration

    Args:
        config_path: Path to config file (not implemented yet, uses env)
        env_file: Path to .env file

    Returns:
        Initialized SpedinesAgent

    Example:
        agent = create_spedines_agent(env_file=".env")

        response = await agent.query("What's the weather like?")
        print(response.response)
    """

    # Load config from environment
    config = SpedinesConfig.from_env(env_file=env_file)

    # Create agent
    return SpedinesAgent(config)
