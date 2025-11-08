#!/usr/bin/env python3
"""
Cache strategies for different Dell-Boca-Boys components
Defines TTL and invalidation policies for memory, workflows, agents, and skills
"""
from typing import Dict, Any
import hashlib
import json


class CacheStrategy:
    """Base cache strategy defining TTL and invalidation rules."""

    namespace: str
    default_ttl: int  # seconds
    max_size: int  # max entries (for LRU eviction)

    @staticmethod
    def build_key(*args, **kwargs) -> str:
        """Build cache key from arguments."""
        key_parts = [str(arg) for arg in args]
        key_parts.extend([f"{k}={v}" for k, v in sorted(kwargs.items())])
        key_str = ":".join(key_parts)
        return hashlib.sha256(key_str.encode()).hexdigest()[:16]


class MemoryQueryStrategy(CacheStrategy):
    """
    Cache strategy for memory retrieval queries.

    High cache rate expected since queries often repeat.
    TTL: 10 minutes (600s)
    """
    namespace = "memory:query"
    default_ttl = 600
    max_size = 10000

    @staticmethod
    def build_key(query: str, memory_type: str, agent_id: str = None) -> str:
        """Build key from query parameters."""
        parts = [query, memory_type]
        if agent_id:
            parts.append(agent_id)
        return hashlib.sha256(":".join(parts).encode()).hexdigest()[:16]

    @staticmethod
    def should_cache(result: Any) -> bool:
        """Only cache successful retrievals with results."""
        if isinstance(result, dict) and result.get("memories"):
            return len(result["memories"]) > 0
        return False


class WorkflowExecutionStrategy(CacheStrategy):
    """
    Cache strategy for workflow execution results.

    Cache completed workflows for audit and replay.
    TTL: 1 hour (3600s)
    """
    namespace = "workflow:execution"
    default_ttl = 3600
    max_size = 5000

    @staticmethod
    def build_key(workflow_id: str, trigger_payload: Dict[str, Any]) -> str:
        """Build key from workflow ID and normalized payload."""
        payload_hash = hashlib.sha256(
            json.dumps(trigger_payload, sort_keys=True).encode()
        ).hexdigest()[:16]
        return f"{workflow_id}:{payload_hash}"

    @staticmethod
    def should_cache(result: Any) -> bool:
        """Only cache successful workflow executions."""
        if isinstance(result, dict):
            return result.get("accepted") is True
        return False


class AgentResponseStrategy(CacheStrategy):
    """
    Cache strategy for agent responses.

    Cache agent outputs for deterministic inputs.
    TTL: 30 minutes (1800s)
    """
    namespace = "agent:response"
    default_ttl = 1800
    max_size = 20000

    @staticmethod
    def build_key(agent_id: str, input_data: Dict[str, Any]) -> str:
        """Build key from agent ID and input hash."""
        input_hash = hashlib.sha256(
            json.dumps(input_data, sort_keys=True).encode()
        ).hexdigest()[:16]
        return f"{agent_id}:{input_hash}"

    @staticmethod
    def should_cache(result: Any) -> bool:
        """Cache all successful agent responses."""
        return result is not None


class SkillExecutionStrategy(CacheStrategy):
    """
    Cache strategy for skill execution results.

    Cache deterministic skill outputs.
    TTL: 1 hour (3600s)
    """
    namespace = "skill:execution"
    default_ttl = 3600
    max_size = 15000

    @staticmethod
    def build_key(skill_id: str, input_params: Dict[str, Any]) -> str:
        """Build key from skill ID and input parameters."""
        params_hash = hashlib.sha256(
            json.dumps(input_params, sort_keys=True).encode()
        ).hexdigest()[:16]
        return f"{skill_id}:{params_hash}"

    @staticmethod
    def should_cache(result: Any) -> bool:
        """Cache successful skill executions."""
        if isinstance(result, dict):
            return result.get("accepted") is True
        return False


class KnowledgeGroundingStrategy(CacheStrategy):
    """
    Cache strategy for knowledge grounding queries.

    Cache evidence retrieval results.
    TTL: 5 minutes (300s) - shorter due to freshness requirements
    """
    namespace = "knowledge:grounding"
    default_ttl = 300
    max_size = 5000

    @staticmethod
    def build_key(query: str, space: str, k: int = 5) -> str:
        """Build key from grounding parameters."""
        return hashlib.sha256(f"{query}:{space}:{k}".encode()).hexdigest()[:16]

    @staticmethod
    def should_cache(result: Any) -> bool:
        """Only cache results with evidence."""
        if isinstance(result, dict) and result.get("evidence"):
            return len(result["evidence"]) > 0
        return False


class ModelTriangulationStrategy(CacheStrategy):
    """
    Cache strategy for multi-model triangulation.

    Cache adjudicated model responses.
    TTL: 15 minutes (900s)
    """
    namespace = "model:triangulation"
    default_ttl = 900
    max_size = 3000

    @staticmethod
    def build_key(task: str, models: list) -> str:
        """Build key from task and model list."""
        models_str = ",".join(sorted(models))
        return hashlib.sha256(f"{task}:{models_str}".encode()).hexdigest()[:16]

    @staticmethod
    def should_cache(result: Any) -> bool:
        """Cache all triangulation results."""
        return isinstance(result, list) and len(result) > 0


# Strategy registry for easy lookup
STRATEGY_REGISTRY = {
    "memory_query": MemoryQueryStrategy,
    "workflow_execution": WorkflowExecutionStrategy,
    "agent_response": AgentResponseStrategy,
    "skill_execution": SkillExecutionStrategy,
    "knowledge_grounding": KnowledgeGroundingStrategy,
    "model_triangulation": ModelTriangulationStrategy,
}


def get_strategy(strategy_name: str) -> CacheStrategy:
    """Get cache strategy by name."""
    if strategy_name not in STRATEGY_REGISTRY:
        raise ValueError(f"Unknown cache strategy: {strategy_name}")
    return STRATEGY_REGISTRY[strategy_name]
