"""
Production-grade Prometheus metrics exporters for Dell Boca Boys V2.
Provides comprehensive observability and monitoring.
"""
import time
import logging
from typing import Optional, Dict, Any, Callable
from functools import wraps
from datetime import datetime

from prometheus_client import (
    Counter, Gauge, Histogram, Summary, Info,
    CollectorRegistry, generate_latest, CONTENT_TYPE_LATEST
)

logger = logging.getLogger(__name__)


# ============================================================================
# Metrics Registry
# ============================================================================

class MetricsCollector:
    """
    Central metrics collector for Dell Boca Boys V2.

    Tracks:
    - Agent performance and health
    - Workflow executions
    - LLM requests and latency
    - Memory operations
    - Cache hit rates
    - API requests and errors
    """

    def __init__(self, registry: Optional[CollectorRegistry] = None):
        """
        Initialize metrics collector.

        Args:
            registry: Prometheus registry (creates new if None)
        """
        self.registry = registry or CollectorRegistry()

        # ====================================================================
        # Agent Metrics
        # ====================================================================

        self.agent_total = Counter(
            'dell_boca_agent_total',
            'Total number of agents created',
            ['agent_type'],
            registry=self.registry
        )

        self.agent_active = Gauge(
            'dell_boca_agent_active',
            'Number of currently active agents',
            ['agent_type'],
            registry=self.registry
        )

        self.agent_health = Gauge(
            'dell_boca_agent_health',
            'Agent health status (1=healthy, 0=unhealthy)',
            ['agent_id', 'agent_type'],
            registry=self.registry
        )

        self.agent_task_duration = Histogram(
            'dell_boca_agent_task_duration_seconds',
            'Agent task execution duration',
            ['agent_type', 'task_type'],
            registry=self.registry,
            buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 30.0, 60.0]
        )

        self.agent_task_total = Counter(
            'dell_boca_agent_task_total',
            'Total agent tasks executed',
            ['agent_type', 'task_type', 'status'],
            registry=self.registry
        )

        # ====================================================================
        # Workflow Metrics
        # ====================================================================

        self.workflow_total = Counter(
            'dell_boca_workflow_total',
            'Total workflows created',
            ['created_by'],
            registry=self.registry
        )

        self.workflow_status = Gauge(
            'dell_boca_workflow_status',
            'Workflows by status',
            ['status'],
            registry=self.registry
        )

        self.workflow_execution_duration = Histogram(
            'dell_boca_workflow_execution_duration_seconds',
            'Workflow execution duration',
            ['workflow_id', 'mode'],
            registry=self.registry,
            buckets=[1.0, 5.0, 10.0, 30.0, 60.0, 120.0, 300.0, 600.0]
        )

        self.workflow_execution_total = Counter(
            'dell_boca_workflow_execution_total',
            'Total workflow executions',
            ['workflow_id', 'mode', 'status'],
            registry=self.registry
        )

        self.workflow_best_practices_score = Gauge(
            'dell_boca_workflow_best_practices_score',
            'Workflow best practices score',
            ['workflow_id'],
            registry=self.registry
        )

        # ====================================================================
        # LLM Metrics
        # ====================================================================

        self.llm_request_total = Counter(
            'dell_boca_llm_request_total',
            'Total LLM requests',
            ['provider', 'model', 'status'],
            registry=self.registry
        )

        self.llm_request_duration = Histogram(
            'dell_boca_llm_request_duration_seconds',
            'LLM request duration',
            ['provider', 'model'],
            registry=self.registry,
            buckets=[0.5, 1.0, 2.0, 5.0, 10.0, 20.0, 30.0]
        )

        self.llm_tokens_used = Counter(
            'dell_boca_llm_tokens_used_total',
            'Total LLM tokens used',
            ['provider', 'model', 'type'],  # type: prompt, completion
            registry=self.registry
        )

        self.llm_cost_estimate = Counter(
            'dell_boca_llm_cost_estimate_usd',
            'Estimated LLM cost in USD',
            ['provider', 'model'],
            registry=self.registry
        )

        # ====================================================================
        # Memory Metrics
        # ====================================================================

        self.memory_operation_total = Counter(
            'dell_boca_memory_operation_total',
            'Total memory operations',
            ['operation', 'provider', 'memory_type', 'status'],
            registry=self.registry
        )

        self.memory_operation_duration = Histogram(
            'dell_boca_memory_operation_duration_seconds',
            'Memory operation duration',
            ['operation', 'provider'],
            registry=self.registry,
            buckets=[0.001, 0.005, 0.01, 0.05, 0.1, 0.5, 1.0, 5.0]
        )

        self.memory_size_bytes = Gauge(
            'dell_boca_memory_size_bytes',
            'Total memory size in bytes',
            ['provider', 'memory_type'],
            registry=self.registry
        )

        self.memory_entries_total = Gauge(
            'dell_boca_memory_entries_total',
            'Total memory entries',
            ['provider', 'memory_type'],
            registry=self.registry
        )

        # ====================================================================
        # Cache Metrics
        # ====================================================================

        self.cache_hits_total = Counter(
            'dell_boca_cache_hits_total',
            'Total cache hits',
            ['namespace'],
            registry=self.registry
        )

        self.cache_misses_total = Counter(
            'dell_boca_cache_misses_total',
            'Total cache misses',
            ['namespace'],
            registry=self.registry
        )

        self.cache_hit_rate = Gauge(
            'dell_boca_cache_hit_rate',
            'Cache hit rate (0-1)',
            ['namespace'],
            registry=self.registry
        )

        self.cache_size_bytes = Gauge(
            'dell_boca_cache_size_bytes',
            'Cache size in bytes',
            [],
            registry=self.registry
        )

        # ====================================================================
        # API Metrics
        # ====================================================================

        self.api_request_total = Counter(
            'dell_boca_api_request_total',
            'Total API requests',
            ['method', 'endpoint', 'status_code'],
            registry=self.registry
        )

        self.api_request_duration = Histogram(
            'dell_boca_api_request_duration_seconds',
            'API request duration',
            ['method', 'endpoint'],
            registry=self.registry,
            buckets=[0.01, 0.05, 0.1, 0.5, 1.0, 2.0, 5.0, 10.0]
        )

        self.api_active_requests = Gauge(
            'dell_boca_api_active_requests',
            'Number of active API requests',
            ['endpoint'],
            registry=self.registry
        )

        self.rate_limit_exceeded_total = Counter(
            'dell_boca_rate_limit_exceeded_total',
            'Total rate limit violations',
            ['endpoint', 'user_id'],
            registry=self.registry
        )

        # ====================================================================
        # Circuit Breaker Metrics
        # ====================================================================

        self.circuit_breaker_state = Gauge(
            'dell_boca_circuit_breaker_state',
            'Circuit breaker state (0=closed, 1=half-open, 2=open)',
            ['name'],
            registry=self.registry
        )

        self.circuit_breaker_success_total = Counter(
            'dell_boca_circuit_breaker_success_total',
            'Circuit breaker successful calls',
            ['name'],
            registry=self.registry
        )

        self.circuit_breaker_failure_total = Counter(
            'dell_boca_circuit_breaker_failure_total',
            'Circuit breaker failed calls',
            ['name'],
            registry=self.registry
        )

        self.circuit_breaker_rejected_total = Counter(
            'dell_boca_circuit_breaker_rejected_total',
            'Circuit breaker rejected calls',
            ['name'],
            registry=self.registry
        )

        # ====================================================================
        # Collective Intelligence Metrics
        # ====================================================================

        self.ci_emergent_behaviors = Gauge(
            'dell_boca_ci_emergent_behaviors_total',
            'Total emergent behaviors detected',
            [],
            registry=self.registry
        )

        self.ci_network_size = Gauge(
            'dell_boca_ci_network_size',
            'Size of agent network',
            [],
            registry=self.registry
        )

        self.ci_emergence_potential = Gauge(
            'dell_boca_ci_emergence_potential',
            'Collective intelligence emergence potential',
            [],
            registry=self.registry
        )

        self.ci_collaboration_events = Counter(
            'dell_boca_ci_collaboration_events_total',
            'Collective intelligence collaboration events',
            ['type'],
            registry=self.registry
        )

        # ====================================================================
        # System Metrics
        # ====================================================================

        self.system_info = Info(
            'dell_boca_system',
            'System information',
            registry=self.registry
        )

        self.system_uptime_seconds = Gauge(
            'dell_boca_system_uptime_seconds',
            'System uptime in seconds',
            registry=self.registry
        )

        # Initialize system info
        self._start_time = time.time()
        self.system_info.info({
            'version': '2.0.0',
            'environment': 'production'
        })

        logger.info("Metrics collector initialized")

    def update_system_uptime(self):
        """Update system uptime metric."""
        uptime = time.time() - self._start_time
        self.system_uptime_seconds.set(uptime)

    def export_metrics(self) -> bytes:
        """
        Export metrics in Prometheus format.

        Returns:
            Prometheus-formatted metrics
        """
        self.update_system_uptime()
        return generate_latest(self.registry)

    def get_content_type(self) -> str:
        """Get Prometheus content type."""
        return CONTENT_TYPE_LATEST


# ============================================================================
# Decorators for Automatic Metrics
# ============================================================================

def track_agent_task(agent_type: str, task_type: str):
    """
    Decorator to track agent task metrics.

    Example:
        @track_agent_task("terry_delmonaco", "workflow_analysis")
        async def analyze_workflow(self, workflow_json):
            ...
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            metrics = get_metrics_collector()
            start_time = time.time()

            try:
                result = await func(*args, **kwargs)
                status = "success"
                return result
            except Exception as e:
                status = "error"
                raise
            finally:
                duration = time.time() - start_time
                metrics.agent_task_duration.labels(
                    agent_type=agent_type,
                    task_type=task_type
                ).observe(duration)
                metrics.agent_task_total.labels(
                    agent_type=agent_type,
                    task_type=task_type,
                    status=status
                ).inc()

        return wrapper
    return decorator


def track_llm_request(provider: str, model: str):
    """
    Decorator to track LLM request metrics.

    Example:
        @track_llm_request("ollama", "qwen2.5-coder:7b")
        async def call_ollama(self, prompt):
            ...
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            metrics = get_metrics_collector()
            start_time = time.time()

            try:
                result = await func(*args, **kwargs)
                status = "success"
                return result
            except Exception as e:
                status = "error"
                raise
            finally:
                duration = time.time() - start_time
                metrics.llm_request_duration.labels(
                    provider=provider,
                    model=model
                ).observe(duration)
                metrics.llm_request_total.labels(
                    provider=provider,
                    model=model,
                    status=status
                ).inc()

        return wrapper
    return decorator


def track_memory_operation(operation: str, provider: str):
    """
    Decorator to track memory operation metrics.

    Example:
        @track_memory_operation("store", "mem0")
        async def store_memory(self, memory_type, content):
            ...
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            metrics = get_metrics_collector()
            start_time = time.time()

            try:
                result = await func(*args, **kwargs)
                status = "success"
                return result
            except Exception as e:
                status = "error"
                raise
            finally:
                duration = time.time() - start_time
                metrics.memory_operation_duration.labels(
                    operation=operation,
                    provider=provider
                ).observe(duration)

        return wrapper
    return decorator


def track_api_request(method: str, endpoint: str):
    """
    Decorator to track API request metrics.

    Example:
        @track_api_request("POST", "/api/workflows")
        async def create_workflow(request):
            ...
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            metrics = get_metrics_collector()
            start_time = time.time()

            # Track active requests
            metrics.api_active_requests.labels(endpoint=endpoint).inc()

            try:
                result = await func(*args, **kwargs)
                status_code = getattr(result, 'status_code', 200)
                return result
            except Exception as e:
                status_code = 500
                raise
            finally:
                duration = time.time() - start_time
                metrics.api_request_duration.labels(
                    method=method,
                    endpoint=endpoint
                ).observe(duration)
                metrics.api_request_total.labels(
                    method=method,
                    endpoint=endpoint,
                    status_code=status_code
                ).inc()
                metrics.api_active_requests.labels(endpoint=endpoint).dec()

        return wrapper
    return decorator


# ============================================================================
# Global Metrics Collector
# ============================================================================

_global_metrics: Optional[MetricsCollector] = None


def init_metrics(registry: Optional[CollectorRegistry] = None) -> MetricsCollector:
    """Initialize global metrics collector."""
    global _global_metrics
    _global_metrics = MetricsCollector(registry=registry)
    return _global_metrics


def get_metrics_collector() -> MetricsCollector:
    """Get global metrics collector instance."""
    if _global_metrics is None:
        return init_metrics()
    return _global_metrics
