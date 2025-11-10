"""
LLM Router - Draft-and-Polish Orchestration
Intelligently routes requests between local Qwen and Gemini
"""

import logging
from typing import Dict, Optional, List, Any, Tuple
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum
import asyncio

from .local import LocalQwenClient, GenerationMetrics as LocalMetrics
from .gemini import GeminiClient, GeminiGenerationMetrics as GeminiMetrics
from .prompts import SpedinesPrompts, PromptTemplate

logger = logging.getLogger(__name__)


class RoutingStrategy(Enum):
    """Available routing strategies"""
    DRAFT_POLISH = "draft_polish"  # Qwen drafts, Gemini polishes (default)
    LOCAL_ONLY = "local_only"  # Only use local Qwen (offline mode)
    GEMINI_ONLY = "gemini_only"  # Only use Gemini (cloud-only mode)
    CONSENSUS = "consensus"  # Both respond, find consensus
    BEST_OF = "best_of"  # Both respond, pick best
    COMPLEXITY_BASED = "complexity_based"  # Route based on complexity threshold


@dataclass
class RoutingMetrics:
    """Metrics for a routed request"""
    strategy: str
    local_used: bool = False
    gemini_used: bool = False
    local_metrics: Optional[LocalMetrics] = None
    gemini_metrics: Optional[GeminiMetrics] = None
    total_latency_ms: float = 0.0
    total_cost_usd: float = 0.0
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    success: bool = True
    error: Optional[str] = None


@dataclass
class RoutingResult:
    """Result from LLM routing"""
    response: str
    strategy: str
    metrics: RoutingMetrics
    metadata: Dict[str, Any] = field(default_factory=dict)


class LLMRouter:
    """
    Intelligent LLM router with Draft-and-Polish orchestration

    Coordinates between local Qwen (fast, free) and Gemini (high-quality, paid)
    to produce optimal responses at minimal cost
    """

    def __init__(
        self,
        local_client: LocalQwenClient,
        gemini_client: Optional[GeminiClient] = None,
        default_strategy: RoutingStrategy = RoutingStrategy.DRAFT_POLISH,
        complexity_threshold: float = 0.6
    ):
        """
        Initialize LLM router

        Args:
            local_client: LocalQwenClient instance
            gemini_client: Optional GeminiClient instance (if None, local-only mode)
            default_strategy: Default routing strategy
            complexity_threshold: Threshold for complexity-based routing (0-1)
        """
        self.local_client = local_client
        self.gemini_client = gemini_client
        self.default_strategy = default_strategy
        self.complexity_threshold = complexity_threshold

        # Metrics
        self.total_requests = 0
        self.strategy_counts = {s.value: 0 for s in RoutingStrategy}

        # If no Gemini client, force local-only mode
        if gemini_client is None and default_strategy != RoutingStrategy.LOCAL_ONLY:
            logger.warning(
                "No Gemini client provided, forcing LOCAL_ONLY strategy"
            )
            self.default_strategy = RoutingStrategy.LOCAL_ONLY

        logger.info(
            f"Initialized LLMRouter: strategy={self.default_strategy.value}, "
            f"complexity_threshold={self.complexity_threshold}"
        )

    async def query(
        self,
        prompt: str,
        template: PromptTemplate = PromptTemplate.GENERAL_QUERY,
        strategy: Optional[RoutingStrategy] = None,
        memory_results: Optional[List[Dict]] = None,
        context: Optional[Dict] = None,
        **kwargs
    ) -> RoutingResult:
        """
        Route a query through the LLM system

        Args:
            prompt: User's query
            template: Prompt template to use
            strategy: Override default routing strategy
            memory_results: Optional memory retrieval results
            context: Optional additional context
            **kwargs: Additional parameters for generation

        Returns:
            RoutingResult with response and metrics
        """

        start_time = datetime.now()
        self.total_requests += 1

        # Determine strategy
        strategy = strategy or self.default_strategy
        self.strategy_counts[strategy.value] += 1

        logger.info(f"Routing query with strategy: {strategy.value}")

        # Initialize metrics
        metrics = RoutingMetrics(strategy=strategy.value)

        try:
            # Route based on strategy
            if strategy == RoutingStrategy.DRAFT_POLISH:
                response = await self._draft_polish(
                    prompt, template, memory_results, context, metrics, **kwargs
                )

            elif strategy == RoutingStrategy.LOCAL_ONLY:
                response = await self._local_only(
                    prompt, template, memory_results, context, metrics, **kwargs
                )

            elif strategy == RoutingStrategy.GEMINI_ONLY:
                response = await self._gemini_only(
                    prompt, template, memory_results, context, metrics, **kwargs
                )

            elif strategy == RoutingStrategy.CONSENSUS:
                response = await self._consensus(
                    prompt, template, memory_results, context, metrics, **kwargs
                )

            elif strategy == RoutingStrategy.BEST_OF:
                response = await self._best_of(
                    prompt, template, memory_results, context, metrics, **kwargs
                )

            elif strategy == RoutingStrategy.COMPLEXITY_BASED:
                response = await self._complexity_based(
                    prompt, template, memory_results, context, metrics, **kwargs
                )

            else:
                raise ValueError(f"Unknown routing strategy: {strategy}")

            # Calculate total metrics
            end_time = datetime.now()
            metrics.total_latency_ms = (end_time - start_time).total_seconds() * 1000
            metrics.success = True

            if metrics.gemini_metrics:
                metrics.total_cost_usd = metrics.gemini_metrics.estimated_cost_usd

            logger.info(
                f"Query completed: {strategy.value} in {metrics.total_latency_ms:.0f}ms "
                f"(${metrics.total_cost_usd:.6f})"
            )

            return RoutingResult(
                response=response,
                strategy=strategy.value,
                metrics=metrics
            )

        except Exception as e:
            # Mark as failed
            end_time = datetime.now()
            metrics.total_latency_ms = (end_time - start_time).total_seconds() * 1000
            metrics.success = False
            metrics.error = str(e)

            logger.error(f"Query failed with strategy {strategy.value}: {e}", exc_info=True)

            # Return error result
            return RoutingResult(
                response=f"Error: {e}",
                strategy=strategy.value,
                metrics=metrics,
                metadata={"error": True}
            )

    async def _draft_polish(
        self,
        prompt: str,
        template: PromptTemplate,
        memory_results: Optional[List[Dict]],
        context: Optional[Dict],
        metrics: RoutingMetrics,
        **kwargs
    ) -> str:
        """
        Draft-and-Polish strategy: Qwen drafts, Gemini polishes

        This is the recommended strategy for most queries:
        - Fast draft from local model (no cost, quick)
        - High-quality polish from Gemini (small cost, accuracy)
        """

        logger.debug("Executing DRAFT_POLISH strategy")

        # Phase 1: Draft with local Qwen
        draft_prompt = SpedinesPrompts.format_draft_prompt(prompt, context)

        if memory_results:
            draft_prompt = SpedinesPrompts.inject_memory_context(draft_prompt, memory_results)

        draft_response, local_metrics = await self.local_client.generate_async(
            prompt=draft_prompt,
            **kwargs
        )

        metrics.local_used = True
        metrics.local_metrics = local_metrics

        logger.debug(f"Draft completed: {local_metrics.total_tokens} tokens in {local_metrics.latency_ms:.0f}ms")

        # Phase 2: Polish with Gemini
        if self.gemini_client is None:
            # No Gemini available, return draft
            logger.warning("Gemini not available, returning draft only")
            return draft_response

        polish_prompt = SpedinesPrompts.format_polish_prompt(
            prompt, draft_response, context
        )

        system_instruction = SpedinesPrompts.get_system_prompt(template, context)

        polished_response, gemini_metrics = await self.gemini_client.generate_async(
            prompt=polish_prompt,
            system_instruction=system_instruction,
            **kwargs
        )

        metrics.gemini_used = True
        metrics.gemini_metrics = gemini_metrics

        logger.debug(
            f"Polish completed: {gemini_metrics.total_tokens} tokens in {gemini_metrics.latency_ms:.0f}ms "
            f"(${gemini_metrics.estimated_cost_usd:.6f})"
        )

        return polished_response

    async def _local_only(
        self,
        prompt: str,
        template: PromptTemplate,
        memory_results: Optional[List[Dict]],
        context: Optional[Dict],
        metrics: RoutingMetrics,
        **kwargs
    ) -> str:
        """Local-only strategy: Only use Qwen (offline mode)"""

        logger.debug("Executing LOCAL_ONLY strategy")

        # Build full prompt
        system_prompt = SpedinesPrompts.get_system_prompt(template, context)
        full_prompt = system_prompt + f"\n\nUser query:\n{prompt}\n\nYour response:"

        if memory_results:
            full_prompt = SpedinesPrompts.inject_memory_context(full_prompt, memory_results)

        response, local_metrics = await self.local_client.generate_async(
            prompt=full_prompt,
            **kwargs
        )

        metrics.local_used = True
        metrics.local_metrics = local_metrics

        return response

    async def _gemini_only(
        self,
        prompt: str,
        template: PromptTemplate,
        memory_results: Optional[List[Dict]],
        context: Optional[Dict],
        metrics: RoutingMetrics,
        **kwargs
    ) -> str:
        """Gemini-only strategy: Only use Gemini (cloud-only mode)"""

        if self.gemini_client is None:
            raise ValueError("Gemini client not available for GEMINI_ONLY strategy")

        logger.debug("Executing GEMINI_ONLY strategy")

        # Build system instruction
        system_instruction = SpedinesPrompts.get_system_prompt(template, context)

        # Build user prompt
        user_prompt = prompt
        if memory_results:
            # Add memory context to user prompt
            memory_text = "\n\nRelevant memory:\n" + "\n".join(
                [m.get('content', '') for m in memory_results]
            )
            user_prompt = memory_text + "\n\n" + prompt

        response, gemini_metrics = await self.gemini_client.generate_async(
            prompt=user_prompt,
            system_instruction=system_instruction,
            **kwargs
        )

        metrics.gemini_used = True
        metrics.gemini_metrics = gemini_metrics

        return response

    async def _consensus(
        self,
        prompt: str,
        template: PromptTemplate,
        memory_results: Optional[List[Dict]],
        context: Optional[Dict],
        metrics: RoutingMetrics,
        **kwargs
    ) -> str:
        """
        Consensus strategy: Both models respond, find consensus

        Good for critical decisions where we want high confidence
        """

        if self.gemini_client is None:
            logger.warning("Gemini not available, falling back to LOCAL_ONLY")
            return await self._local_only(prompt, template, memory_results, context, metrics, **kwargs)

        logger.debug("Executing CONSENSUS strategy")

        # Build prompts
        system_prompt = SpedinesPrompts.get_system_prompt(template, context)
        full_prompt = system_prompt + f"\n\nUser query:\n{prompt}\n\nYour response:"

        if memory_results:
            full_prompt = SpedinesPrompts.inject_memory_context(full_prompt, memory_results)

        # Query both models in parallel
        local_task = self.local_client.generate_async(prompt=full_prompt, **kwargs)
        gemini_task = self.gemini_client.generate_async(
            prompt=prompt,
            system_instruction=system_prompt,
            **kwargs
        )

        results = await asyncio.gather(local_task, gemini_task, return_exceptions=True)

        # Handle failures
        if isinstance(results[0], Exception):
            logger.warning(f"Local model failed in consensus: {results[0]}")
            if isinstance(results[1], Exception):
                raise Exception("Both models failed in consensus mode")
            # Only Gemini succeeded
            _, gemini_metrics = results[1]
            metrics.gemini_used = True
            metrics.gemini_metrics = gemini_metrics
            return _[0]

        if isinstance(results[1], Exception):
            logger.warning(f"Gemini failed in consensus: {results[1]}")
            # Only local succeeded
            local_response, local_metrics = results[0]
            metrics.local_used = True
            metrics.local_metrics = local_metrics
            return local_response

        # Both succeeded - find consensus
        local_response, local_metrics = results[0]
        gemini_response, gemini_metrics = results[1]

        metrics.local_used = True
        metrics.gemini_used = True
        metrics.local_metrics = local_metrics
        metrics.gemini_metrics = gemini_metrics

        # Use Gemini to synthesize consensus
        consensus_prompt = SpedinesPrompts.format_consensus_prompt(
            prompt, local_response, gemini_response,
            source_a="Local Qwen", source_b="Gemini"
        )

        consensus_response, consensus_metrics = await self.gemini_client.generate_async(
            prompt=consensus_prompt
        )

        # Update Gemini metrics (second call)
        metrics.gemini_metrics.total_tokens += consensus_metrics.total_tokens
        metrics.gemini_metrics.estimated_cost_usd += consensus_metrics.estimated_cost_usd

        return consensus_response

    async def _best_of(
        self,
        prompt: str,
        template: PromptTemplate,
        memory_results: Optional[List[Dict]],
        context: Optional[Dict],
        metrics: RoutingMetrics,
        **kwargs
    ) -> str:
        """
        Best-of strategy: Both models respond, pick best

        Similar to consensus but faster (no synthesis step)
        """

        if self.gemini_client is None:
            logger.warning("Gemini not available, falling back to LOCAL_ONLY")
            return await self._local_only(prompt, template, memory_results, context, metrics, **kwargs)

        logger.debug("Executing BEST_OF strategy")

        # Build prompts
        system_prompt = SpedinesPrompts.get_system_prompt(template, context)
        full_prompt = system_prompt + f"\n\nUser query:\n{prompt}\n\nYour response:"

        if memory_results:
            full_prompt = SpedinesPrompts.inject_memory_context(full_prompt, memory_results)

        # Query both models in parallel
        local_task = self.local_client.generate_async(prompt=full_prompt, **kwargs)
        gemini_task = self.gemini_client.generate_async(
            prompt=prompt,
            system_instruction=system_prompt,
            **kwargs
        )

        results = await asyncio.gather(local_task, gemini_task, return_exceptions=True)

        # Handle failures
        if isinstance(results[0], Exception) and isinstance(results[1], Exception):
            raise Exception("Both models failed in best-of mode")

        if isinstance(results[0], Exception):
            gemini_response, gemini_metrics = results[1]
            metrics.gemini_used = True
            metrics.gemini_metrics = gemini_metrics
            return gemini_response

        if isinstance(results[1], Exception):
            local_response, local_metrics = results[0]
            metrics.local_used = True
            metrics.local_metrics = local_metrics
            return local_response

        # Both succeeded - pick best (simple heuristic: prefer Gemini)
        local_response, local_metrics = results[0]
        gemini_response, gemini_metrics = results[1]

        metrics.local_used = True
        metrics.gemini_used = True
        metrics.local_metrics = local_metrics
        metrics.gemini_metrics = gemini_metrics

        # Simple heuristic: prefer Gemini for quality
        # Could be made more sophisticated with quality scoring
        logger.debug("Selecting Gemini response as best")
        return gemini_response

    async def _complexity_based(
        self,
        prompt: str,
        template: PromptTemplate,
        memory_results: Optional[List[Dict]],
        context: Optional[Dict],
        metrics: RoutingMetrics,
        **kwargs
    ) -> str:
        """
        Complexity-based strategy: Route based on query complexity

        Simple queries -> Local only (fast, free)
        Complex queries -> Draft-and-Polish (quality, small cost)
        """

        logger.debug("Executing COMPLEXITY_BASED strategy")

        # Estimate complexity (simple heuristic)
        complexity = self._estimate_complexity(prompt, template)

        logger.info(f"Estimated complexity: {complexity:.2f} (threshold: {self.complexity_threshold})")

        if complexity < self.complexity_threshold:
            # Simple query - use local only
            logger.debug("Query is simple, using LOCAL_ONLY")
            return await self._local_only(prompt, template, memory_results, context, metrics, **kwargs)
        else:
            # Complex query - use draft-and-polish
            logger.debug("Query is complex, using DRAFT_POLISH")
            return await self._draft_polish(prompt, template, memory_results, context, metrics, **kwargs)

    def _estimate_complexity(self, prompt: str, template: PromptTemplate) -> float:
        """
        Estimate query complexity (0-1 scale)

        Simple heuristic based on:
        - Prompt length
        - Template type
        - Keywords indicating complexity

        Returns:
            Float from 0 (simple) to 1 (complex)
        """

        complexity = 0.0

        # Length factor (longer prompts tend to be more complex)
        length = len(prompt)
        if length < 50:
            complexity += 0.1
        elif length < 150:
            complexity += 0.3
        elif length < 300:
            complexity += 0.5
        else:
            complexity += 0.7

        # Template factor
        template_complexity = {
            PromptTemplate.GENERAL_QUERY: 0.2,
            PromptTemplate.CODE_GENERATION: 0.6,
            PromptTemplate.WORKFLOW_DESIGN: 0.7,
            PromptTemplate.DATA_ANALYSIS: 0.8,
            PromptTemplate.REFLECTION: 0.5,
            PromptTemplate.SELF_CRITIQUE: 0.6,
            PromptTemplate.LEARNING: 0.5,
            PromptTemplate.RESEARCH: 0.9
        }
        complexity += template_complexity.get(template, 0.5) * 0.5

        # Keyword factor
        complex_keywords = [
            "analyze", "design", "architecture", "implement", "optimize",
            "compare", "evaluate", "research", "synthesize", "critique"
        ]

        prompt_lower = prompt.lower()
        keyword_matches = sum(1 for kw in complex_keywords if kw in prompt_lower)
        complexity += min(keyword_matches * 0.1, 0.3)

        # Normalize to 0-1
        return min(complexity, 1.0)

    def get_metrics(self) -> Dict[str, Any]:
        """Get router metrics"""

        return {
            "total_requests": self.total_requests,
            "strategy_counts": self.strategy_counts,
            "default_strategy": self.default_strategy.value,
            "local_metrics": self.local_client.get_metrics(),
            "gemini_metrics": self.gemini_client.get_metrics() if self.gemini_client else None
        }

    def health_check(self) -> Dict[str, Any]:
        """Check health of all LLM clients"""

        health = {
            "local": self.local_client.health_check()
        }

        if self.gemini_client:
            health["gemini"] = self.gemini_client.health_check()

        health["overall_status"] = "healthy" if all(
            h.get("status") == "healthy" for h in health.values()
        ) else "degraded"

        return health


# Convenience function

async def create_router_from_config(config: Dict) -> LLMRouter:
    """
    Create LLMRouter from configuration

    Args:
        config: Configuration dictionary with llm settings

    Returns:
        Initialized LLMRouter
    """

    from .local import create_local_client_from_config
    from .gemini import create_gemini_client_from_config

    # Create local client
    local_config = {
        "endpoint": config.get("qwen_endpoint", "http://localhost:11434/v1"),
        "model_name": config.get("qwen_model", "qwen2.5-coder:32b"),
        "max_tokens": config.get("max_tokens", 4096),
        "temperature": config.get("qwen_temperature", 0.1)
    }
    local_client = create_local_client_from_config(local_config)

    # Create Gemini client if API key provided
    gemini_client = None
    if config.get("gemini_api_key"):
        gemini_config = {
            "api_key": config["gemini_api_key"],
            "model_name": config.get("gemini_model", "gemini-2.0-flash-exp"),
            "max_tokens": config.get("gemini_max_tokens", 8192),
            "temperature": config.get("gemini_temperature", 0.3)
        }
        gemini_client = create_gemini_client_from_config(gemini_config)

    # Determine strategy
    strategy_str = config.get("routing_strategy", "draft_polish")
    strategy_map = {s.value: s for s in RoutingStrategy}
    strategy = strategy_map.get(strategy_str, RoutingStrategy.DRAFT_POLISH)

    # Create router
    router = LLMRouter(
        local_client=local_client,
        gemini_client=gemini_client,
        default_strategy=strategy,
        complexity_threshold=config.get("complexity_threshold", 0.6)
    )

    return router
