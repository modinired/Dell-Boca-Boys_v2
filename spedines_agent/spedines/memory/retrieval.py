"""
Memory Retrieval for RAG (Retrieval-Augmented Generation)
Intelligent retrieval and formatting of relevant memories
"""

import logging
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum

from .chroma import ChromaMemoryStore

logger = logging.getLogger(__name__)


class RetrievalStrategy(Enum):
    """Strategies for memory retrieval"""
    SEMANTIC = "semantic"  # Pure semantic similarity
    RECENT = "recent"  # Most recent memories
    HYBRID = "hybrid"  # Combine semantic + recency
    FILTERED = "filtered"  # Semantic with metadata filters


@dataclass
class RetrievalConfig:
    """Configuration for memory retrieval"""
    strategy: RetrievalStrategy = RetrievalStrategy.HYBRID
    top_k: int = 5  # Number of memories to retrieve
    min_similarity: float = 0.7  # Minimum similarity threshold (0-1)
    recency_weight: float = 0.3  # Weight for recency in hybrid mode (0-1)
    max_age_days: Optional[int] = None  # Filter out memories older than this
    source_filter: Optional[str] = None  # Filter by source metadata
    include_metadata: bool = True  # Include metadata in results


@dataclass
class RetrievalResult:
    """Result from memory retrieval"""
    content: str
    similarity: float
    metadata: Dict[str, Any]
    memory_id: str
    rank: int  # Ranking position (1 = best match)


class MemoryRetriever:
    """
    Intelligent memory retrieval for RAG

    Retrieves relevant memories and formats them for LLM context
    """

    def __init__(
        self,
        memory_store: ChromaMemoryStore,
        config: Optional[RetrievalConfig] = None
    ):
        """
        Initialize memory retriever

        Args:
            memory_store: ChromaMemoryStore instance
            config: Optional retrieval configuration
        """

        self.memory_store = memory_store
        self.config = config or RetrievalConfig()

        logger.info(
            f"Initialized MemoryRetriever: strategy={self.config.strategy.value}, "
            f"top_k={self.config.top_k}, min_similarity={self.config.min_similarity}"
        )

        # Metrics
        self.total_retrievals = 0
        self.total_memories_retrieved = 0

    def retrieve(
        self,
        query: str,
        top_k: Optional[int] = None,
        strategy: Optional[RetrievalStrategy] = None,
        metadata_filter: Optional[Dict] = None
    ) -> List[RetrievalResult]:
        """
        Retrieve relevant memories for a query

        Args:
            query: Query text
            top_k: Override default top_k
            strategy: Override default strategy
            metadata_filter: Optional metadata filter

        Returns:
            List of RetrievalResult objects, sorted by relevance
        """

        strategy = strategy or self.config.strategy
        top_k = top_k or self.config.top_k

        logger.debug(f"Retrieving memories for query (strategy={strategy.value}, top_k={top_k})")

        self.total_retrievals += 1

        try:
            if strategy == RetrievalStrategy.SEMANTIC:
                results = self._retrieve_semantic(query, top_k, metadata_filter)

            elif strategy == RetrievalStrategy.RECENT:
                results = self._retrieve_recent(top_k, metadata_filter)

            elif strategy == RetrievalStrategy.HYBRID:
                results = self._retrieve_hybrid(query, top_k, metadata_filter)

            elif strategy == RetrievalStrategy.FILTERED:
                results = self._retrieve_filtered(query, top_k, metadata_filter)

            else:
                raise ValueError(f"Unknown retrieval strategy: {strategy}")

            # Filter by minimum similarity
            results = [r for r in results if r.similarity >= self.config.min_similarity]

            # Filter by age if configured
            if self.config.max_age_days:
                results = self._filter_by_age(results, self.config.max_age_days)

            # Update metrics
            self.total_memories_retrieved += len(results)

            logger.info(f"Retrieved {len(results)} relevant memories")

            return results

        except Exception as e:
            logger.error(f"Memory retrieval failed: {e}", exc_info=True)
            return []

    def _retrieve_semantic(
        self,
        query: str,
        top_k: int,
        metadata_filter: Optional[Dict]
    ) -> List[RetrievalResult]:
        """Retrieve using pure semantic similarity"""

        where = self._build_where_filter(metadata_filter)

        raw_results = self.memory_store.query(
            query_text=query,
            n_results=top_k,
            where=where
        )

        return self._format_results(raw_results)

    def _retrieve_recent(
        self,
        top_k: int,
        metadata_filter: Optional[Dict]
    ) -> List[RetrievalResult]:
        """Retrieve most recent memories"""

        source = metadata_filter.get("source") if metadata_filter else None

        recent_memories = self.memory_store.get_recent_memories(
            n=top_k,
            source=source
        )

        # Convert to RetrievalResult format (similarity = 1.0 for all)
        results = []
        for rank, memory in enumerate(recent_memories, 1):
            results.append(RetrievalResult(
                content=memory["document"],
                similarity=1.0,  # No semantic comparison
                metadata=memory["metadata"],
                memory_id=memory["id"],
                rank=rank
            ))

        return results

    def _retrieve_hybrid(
        self,
        query: str,
        top_k: int,
        metadata_filter: Optional[Dict]
    ) -> List[RetrievalResult]:
        """
        Retrieve using hybrid semantic + recency scoring

        Combines semantic similarity with recency boost
        """

        # Get more results than needed for re-ranking
        retrieve_k = min(top_k * 3, 50)

        where = self._build_where_filter(metadata_filter)

        raw_results = self.memory_store.query(
            query_text=query,
            n_results=retrieve_k,
            where=where
        )

        results = self._format_results(raw_results)

        # Calculate hybrid scores
        now = datetime.now()
        recency_weight = self.config.recency_weight
        semantic_weight = 1.0 - recency_weight

        for result in results:
            # Parse timestamp
            timestamp_str = result.metadata.get("timestamp", "")
            try:
                timestamp = datetime.fromisoformat(timestamp_str)
                age_days = (now - timestamp).days
                # Recency score: 1.0 for today, decays exponentially
                recency_score = max(0.0, 1.0 - (age_days / 365.0))
            except Exception:
                recency_score = 0.5  # Default if no valid timestamp

            # Hybrid score
            hybrid_score = (
                semantic_weight * result.similarity +
                recency_weight * recency_score
            )

            result.similarity = hybrid_score

        # Re-rank by hybrid score
        results.sort(key=lambda r: r.similarity, reverse=True)

        # Update ranks
        for rank, result in enumerate(results[:top_k], 1):
            result.rank = rank

        return results[:top_k]

    def _retrieve_filtered(
        self,
        query: str,
        top_k: int,
        metadata_filter: Optional[Dict]
    ) -> List[RetrievalResult]:
        """Retrieve with strict metadata filtering"""

        if not metadata_filter:
            # No filter provided, fall back to semantic
            return self._retrieve_semantic(query, top_k, None)

        where = self._build_where_filter(metadata_filter)

        raw_results = self.memory_store.query(
            query_text=query,
            n_results=top_k,
            where=where
        )

        return self._format_results(raw_results)

    def _format_results(self, raw_results: Dict) -> List[RetrievalResult]:
        """Convert raw ChromaDB results to RetrievalResult objects"""

        results = []

        for rank, (doc, metadata, distance, memory_id) in enumerate(
            zip(
                raw_results["documents"],
                raw_results["metadatas"],
                raw_results["distances"],
                raw_results["ids"]
            ),
            1
        ):
            # Convert distance to similarity (assuming cosine distance)
            # Cosine distance is 1 - cosine_similarity, so similarity = 1 - distance
            similarity = max(0.0, 1.0 - distance)

            results.append(RetrievalResult(
                content=doc,
                similarity=similarity,
                metadata=metadata,
                memory_id=memory_id,
                rank=rank
            ))

        return results

    def _build_where_filter(self, metadata_filter: Optional[Dict]) -> Optional[Dict]:
        """Build ChromaDB where filter from metadata filter"""

        where = {}

        # Add source filter if configured
        if self.config.source_filter:
            where["source"] = self.config.source_filter

        # Add user-provided filters
        if metadata_filter:
            where.update(metadata_filter)

        return where if where else None

    def _filter_by_age(
        self,
        results: List[RetrievalResult],
        max_age_days: int
    ) -> List[RetrievalResult]:
        """Filter out memories older than max_age_days"""

        cutoff = datetime.now() - timedelta(days=max_age_days)

        filtered = []
        for result in results:
            timestamp_str = result.metadata.get("timestamp", "")

            try:
                timestamp = datetime.fromisoformat(timestamp_str)
                if timestamp >= cutoff:
                    filtered.append(result)
            except Exception:
                # Keep if timestamp can't be parsed
                filtered.append(result)

        return filtered

    def format_for_prompt(
        self,
        results: List[RetrievalResult],
        max_results: Optional[int] = None,
        include_similarity: bool = False,
        include_metadata: bool = False
    ) -> str:
        """
        Format retrieval results for LLM prompt

        Args:
            results: List of RetrievalResult objects
            max_results: Maximum results to include
            include_similarity: Include similarity scores
            include_metadata: Include metadata

        Returns:
            Formatted string for prompt injection
        """

        if not results:
            return ""

        if max_results:
            results = results[:max_results]

        formatted_parts = []

        for result in results:
            part = f"[Memory {result.rank}]"

            if include_similarity:
                part += f" (Relevance: {result.similarity:.2f})"

            part += f"\n{result.content}"

            if include_metadata and result.metadata:
                # Format relevant metadata
                metadata_str = self._format_metadata(result.metadata)
                if metadata_str:
                    part += f"\n{metadata_str}"

            formatted_parts.append(part)

        return "\n\n".join(formatted_parts)

    def _format_metadata(self, metadata: Dict) -> str:
        """Format metadata for display"""

        important_keys = ["source", "timestamp", "type", "tags"]

        parts = []
        for key in important_keys:
            if key in metadata:
                value = metadata[key]

                # Format timestamp nicely
                if key == "timestamp":
                    try:
                        dt = datetime.fromisoformat(value)
                        value = dt.strftime("%Y-%m-%d %H:%M")
                    except Exception:
                        pass

                parts.append(f"{key.capitalize()}: {value}")

        return "  |  ".join(parts) if parts else ""

    def get_conversation_context(
        self,
        query: str,
        top_k: int = 3
    ) -> List[RetrievalResult]:
        """
        Get conversation context specifically

        Retrieves relevant past conversations

        Args:
            query: Current query
            top_k: Number of conversations to retrieve

        Returns:
            List of relevant conversation memories
        """

        return self.retrieve(
            query=query,
            top_k=top_k,
            metadata_filter={"source": "conversation"}
        )

    def get_learned_knowledge(
        self,
        query: str,
        top_k: int = 5
    ) -> List[RetrievalResult]:
        """
        Get learned knowledge specifically

        Retrieves relevant learned information (not conversations)

        Args:
            query: Query for knowledge
            top_k: Number of knowledge items to retrieve

        Returns:
            List of relevant knowledge memories
        """

        return self.retrieve(
            query=query,
            top_k=top_k,
            metadata_filter={"source": "learned"}
        )

    def get_context_for_query(
        self,
        query: str,
        include_conversations: bool = True,
        include_knowledge: bool = True
    ) -> Dict[str, List[RetrievalResult]]:
        """
        Get comprehensive context for a query

        Retrieves both conversation history and learned knowledge

        Args:
            query: User query
            include_conversations: Include conversation context
            include_knowledge: Include learned knowledge

        Returns:
            Dictionary with conversation and knowledge results
        """

        context = {}

        if include_conversations:
            context["conversations"] = self.get_conversation_context(query, top_k=2)

        if include_knowledge:
            context["knowledge"] = self.get_learned_knowledge(query, top_k=3)

        return context

    def format_full_context(
        self,
        query: str,
        include_conversations: bool = True,
        include_knowledge: bool = True
    ) -> str:
        """
        Get and format full context for LLM prompt

        Args:
            query: User query
            include_conversations: Include conversation history
            include_knowledge: Include learned knowledge

        Returns:
            Formatted context string ready for prompt
        """

        context = self.get_context_for_query(
            query,
            include_conversations,
            include_knowledge
        )

        parts = []

        if include_conversations and context.get("conversations"):
            conv_text = self.format_for_prompt(
                context["conversations"],
                include_metadata=True
            )
            if conv_text:
                parts.append(f"### Relevant Past Conversations:\n{conv_text}")

        if include_knowledge and context.get("knowledge"):
            knowledge_text = self.format_for_prompt(
                context["knowledge"],
                include_metadata=True
            )
            if knowledge_text:
                parts.append(f"### Relevant Knowledge:\n{knowledge_text}")

        return "\n\n".join(parts) if parts else ""

    def get_metrics(self) -> Dict[str, Any]:
        """Get retrieval metrics"""

        avg_retrieved = (
            self.total_memories_retrieved / max(self.total_retrievals, 1)
        )

        return {
            "total_retrievals": self.total_retrievals,
            "total_memories_retrieved": self.total_memories_retrieved,
            "avg_memories_per_retrieval": avg_retrieved,
            "config": {
                "strategy": self.config.strategy.value,
                "top_k": self.config.top_k,
                "min_similarity": self.config.min_similarity
            }
        }


# Factory function

def create_memory_retriever(
    memory_store: ChromaMemoryStore,
    strategy: str = "hybrid",
    top_k: int = 5,
    min_similarity: float = 0.7,
    **kwargs
) -> MemoryRetriever:
    """
    Create memory retriever with configuration

    Args:
        memory_store: ChromaMemoryStore instance
        strategy: Retrieval strategy ("semantic", "recent", "hybrid", "filtered")
        top_k: Number of results to retrieve
        min_similarity: Minimum similarity threshold
        **kwargs: Additional config parameters

    Returns:
        Initialized MemoryRetriever
    """

    strategy_map = {s.value: s for s in RetrievalStrategy}
    strategy_enum = strategy_map.get(strategy, RetrievalStrategy.HYBRID)

    config = RetrievalConfig(
        strategy=strategy_enum,
        top_k=top_k,
        min_similarity=min_similarity,
        **kwargs
    )

    return MemoryRetriever(memory_store, config)
