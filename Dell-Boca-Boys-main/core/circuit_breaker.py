"""
Production-grade circuit breaker implementation for Dell Boca Boys V2.
Provides fault tolerance, automatic recovery, and metrics tracking.
"""
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Callable, Optional, Any, Dict
from enum import Enum
from dataclasses import dataclass, field
from functools import wraps
import time

from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    before_sleep_log
)

from core.exceptions import (
    LLMProviderError,
    LLMTimeoutError,
    DatabaseConnectionError,
    CacheConnectionError,
    ExternalServiceError
)

logger = logging.getLogger(__name__)


class CircuitState(Enum):
    """Circuit breaker states."""
    CLOSED = "closed"  # Normal operation
    OPEN = "open"      # Failing, rejecting requests
    HALF_OPEN = "half_open"  # Testing recovery


@dataclass
class CircuitBreakerMetrics:
    """Metrics for circuit breaker monitoring."""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    rejected_requests: int = 0  # Rejected due to open circuit
    last_failure_time: Optional[datetime] = None
    last_success_time: Optional[datetime] = None
    consecutive_failures: int = 0
    consecutive_successes: int = 0
    state_transitions: list = field(default_factory=list)

    @property
    def success_rate(self) -> float:
        """Calculate success rate."""
        if self.total_requests == 0:
            return 0.0
        return self.successful_requests / self.total_requests

    @property
    def failure_rate(self) -> float:
        """Calculate failure rate."""
        return 1.0 - self.success_rate


class CircuitBreaker:
    """
    Circuit breaker implementation with automatic recovery.

    The circuit breaker transitions between three states:
    - CLOSED: Normal operation, requests pass through
    - OPEN: Too many failures, requests are rejected
    - HALF_OPEN: Testing if service has recovered

    Transitions:
    - CLOSED -> OPEN: After failure_threshold consecutive failures
    - OPEN -> HALF_OPEN: After timeout_duration
    - HALF_OPEN -> CLOSED: After success_threshold consecutive successes
    - HALF_OPEN -> OPEN: On any failure
    """

    def __init__(
        self,
        name: str,
        failure_threshold: int = 5,
        success_threshold: int = 2,
        timeout_duration: int = 60,
        excluded_exceptions: tuple = ()
    ):
        """
        Initialize circuit breaker.

        Args:
            name: Circuit breaker identifier
            failure_threshold: Consecutive failures before opening circuit
            success_threshold: Consecutive successes to close from half-open
            timeout_duration: Seconds to wait before trying half-open
            excluded_exceptions: Exception types that don't trigger the circuit
        """
        self.name = name
        self.failure_threshold = failure_threshold
        self.success_threshold = success_threshold
        self.timeout_duration = timeout_duration
        self.excluded_exceptions = excluded_exceptions

        self.state = CircuitState.CLOSED
        self.metrics = CircuitBreakerMetrics()
        self.opened_at: Optional[datetime] = None
        self._lock = asyncio.Lock()

        logger.info(
            f"Circuit breaker '{name}' initialized: "
            f"failure_threshold={failure_threshold}, "
            f"success_threshold={success_threshold}, "
            f"timeout_duration={timeout_duration}s"
        )

    async def call(self, func: Callable, *args, **kwargs) -> Any:
        """
        Execute function through circuit breaker.

        Args:
            func: Function to execute
            *args: Positional arguments
            **kwargs: Keyword arguments

        Returns:
            Function result

        Raises:
            CircuitBreakerOpenError: If circuit is open
            Original exception: If function fails
        """
        async with self._lock:
            # Check if circuit should transition to half-open
            if self.state == CircuitState.OPEN:
                if self._should_attempt_reset():
                    self._transition_to_half_open()
                else:
                    self.metrics.rejected_requests += 1
                    raise CircuitBreakerOpenError(
                        f"Circuit breaker '{self.name}' is OPEN",
                        retry_after=self._time_until_retry()
                    )

        # Execute function
        try:
            if asyncio.iscoroutinefunction(func):
                result = await func(*args, **kwargs)
            else:
                result = func(*args, **kwargs)

            await self._on_success()
            return result

        except Exception as e:
            # Don't count excluded exceptions as failures
            if isinstance(e, self.excluded_exceptions):
                raise

            await self._on_failure(e)
            raise

    async def _on_success(self):
        """Handle successful execution."""
        async with self._lock:
            self.metrics.total_requests += 1
            self.metrics.successful_requests += 1
            self.metrics.consecutive_successes += 1
            self.metrics.consecutive_failures = 0
            self.metrics.last_success_time = datetime.utcnow()

            # Transition from half-open to closed after enough successes
            if self.state == CircuitState.HALF_OPEN:
                if self.metrics.consecutive_successes >= self.success_threshold:
                    self._transition_to_closed()

    async def _on_failure(self, exception: Exception):
        """Handle failed execution."""
        async with self._lock:
            self.metrics.total_requests += 1
            self.metrics.failed_requests += 1
            self.metrics.consecutive_failures += 1
            self.metrics.consecutive_successes = 0
            self.metrics.last_failure_time = datetime.utcnow()

            logger.warning(
                f"Circuit breaker '{self.name}' recorded failure "
                f"({self.metrics.consecutive_failures}/{self.failure_threshold}): "
                f"{type(exception).__name__}: {str(exception)}"
            )

            # Open circuit if threshold exceeded
            if self.state == CircuitState.CLOSED:
                if self.metrics.consecutive_failures >= self.failure_threshold:
                    self._transition_to_open()
            elif self.state == CircuitState.HALF_OPEN:
                # Any failure in half-open state reopens the circuit
                self._transition_to_open()

    def _should_attempt_reset(self) -> bool:
        """Check if enough time has passed to attempt reset."""
        if self.opened_at is None:
            return False
        elapsed = (datetime.utcnow() - self.opened_at).total_seconds()
        return elapsed >= self.timeout_duration

    def _time_until_retry(self) -> int:
        """Calculate seconds until retry is allowed."""
        if self.opened_at is None:
            return 0
        elapsed = (datetime.utcnow() - self.opened_at).total_seconds()
        remaining = max(0, self.timeout_duration - elapsed)
        return int(remaining)

    def _transition_to_open(self):
        """Transition to OPEN state."""
        previous_state = self.state
        self.state = CircuitState.OPEN
        self.opened_at = datetime.utcnow()

        self.metrics.state_transitions.append({
            "from": previous_state.value,
            "to": CircuitState.OPEN.value,
            "timestamp": datetime.utcnow().isoformat(),
            "consecutive_failures": self.metrics.consecutive_failures
        })

        logger.error(
            f"Circuit breaker '{self.name}' transitioned to OPEN "
            f"after {self.metrics.consecutive_failures} consecutive failures"
        )

    def _transition_to_half_open(self):
        """Transition to HALF_OPEN state."""
        previous_state = self.state
        self.state = CircuitState.HALF_OPEN

        self.metrics.state_transitions.append({
            "from": previous_state.value,
            "to": CircuitState.HALF_OPEN.value,
            "timestamp": datetime.utcnow().isoformat()
        })

        logger.info(f"Circuit breaker '{self.name}' transitioned to HALF_OPEN (testing recovery)")

    def _transition_to_closed(self):
        """Transition to CLOSED state."""
        previous_state = self.state
        self.state = CircuitState.CLOSED
        self.opened_at = None
        self.metrics.consecutive_failures = 0

        self.metrics.state_transitions.append({
            "from": previous_state.value,
            "to": CircuitState.CLOSED.value,
            "timestamp": datetime.utcnow().isoformat(),
            "consecutive_successes": self.metrics.consecutive_successes
        })

        logger.info(
            f"Circuit breaker '{self.name}' transitioned to CLOSED "
            f"after {self.metrics.consecutive_successes} consecutive successes"
        )

    def get_state(self) -> CircuitState:
        """Get current circuit state."""
        return self.state

    def get_metrics(self) -> Dict[str, Any]:
        """Get circuit breaker metrics."""
        return {
            "name": self.name,
            "state": self.state.value,
            "total_requests": self.metrics.total_requests,
            "successful_requests": self.metrics.successful_requests,
            "failed_requests": self.metrics.failed_requests,
            "rejected_requests": self.metrics.rejected_requests,
            "success_rate": self.metrics.success_rate,
            "failure_rate": self.metrics.failure_rate,
            "consecutive_failures": self.metrics.consecutive_failures,
            "consecutive_successes": self.metrics.consecutive_successes,
            "last_failure_time": self.metrics.last_failure_time.isoformat() if self.metrics.last_failure_time else None,
            "last_success_time": self.metrics.last_success_time.isoformat() if self.metrics.last_success_time else None,
            "opened_at": self.opened_at.isoformat() if self.opened_at else None,
            "time_until_retry": self._time_until_retry() if self.state == CircuitState.OPEN else None,
            "state_transitions": self.metrics.state_transitions[-10:]  # Last 10 transitions
        }

    async def reset(self):
        """Manually reset circuit breaker to CLOSED state."""
        async with self._lock:
            previous_state = self.state
            self.state = CircuitState.CLOSED
            self.opened_at = None
            self.metrics.consecutive_failures = 0
            self.metrics.consecutive_successes = 0

            logger.info(f"Circuit breaker '{self.name}' manually reset from {previous_state.value} to CLOSED")


class CircuitBreakerOpenError(Exception):
    """Raised when circuit breaker is open."""

    def __init__(self, message: str, retry_after: int):
        super().__init__(message)
        self.retry_after = retry_after


# ============================================================================
# Circuit Breaker Decorator
# ============================================================================

def with_circuit_breaker(
    name: str,
    failure_threshold: int = 5,
    success_threshold: int = 2,
    timeout_duration: int = 60,
    excluded_exceptions: tuple = ()
):
    """
    Decorator to wrap function with circuit breaker.

    Args:
        name: Circuit breaker identifier
        failure_threshold: Consecutive failures before opening
        success_threshold: Consecutive successes to close from half-open
        timeout_duration: Seconds to wait before trying half-open
        excluded_exceptions: Exceptions that don't trigger the circuit

    Example:
        @with_circuit_breaker(
            name="ollama_api",
            failure_threshold=3,
            timeout_duration=30
        )
        async def call_ollama(prompt: str):
            return await ollama_client.generate(prompt)
    """
    # Store circuit breakers globally
    if not hasattr(with_circuit_breaker, '_breakers'):
        with_circuit_breaker._breakers = {}

    if name not in with_circuit_breaker._breakers:
        with_circuit_breaker._breakers[name] = CircuitBreaker(
            name=name,
            failure_threshold=failure_threshold,
            success_threshold=success_threshold,
            timeout_duration=timeout_duration,
            excluded_exceptions=excluded_exceptions
        )

    breaker = with_circuit_breaker._breakers[name]

    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            return await breaker.call(func, *args, **kwargs)
        return wrapper
    return decorator


def get_circuit_breaker(name: str) -> Optional[CircuitBreaker]:
    """Get circuit breaker instance by name."""
    if hasattr(with_circuit_breaker, '_breakers'):
        return with_circuit_breaker._breakers.get(name)
    return None


def get_all_circuit_breakers() -> Dict[str, CircuitBreaker]:
    """Get all circuit breaker instances."""
    if hasattr(with_circuit_breaker, '_breakers'):
        return with_circuit_breaker._breakers.copy()
    return {}


# ============================================================================
# Retry Decorators with Exponential Backoff
# ============================================================================

# Retry for LLM providers
retry_llm_provider = retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=30),
    retry=retry_if_exception_type((LLMProviderError, LLMTimeoutError)),
    before_sleep=before_sleep_log(logger, logging.WARNING),
    reraise=True
)

# Retry for database operations
retry_database = retry(
    stop=stop_after_attempt(5),
    wait=wait_exponential(multiplier=1, min=1, max=10),
    retry=retry_if_exception_type(DatabaseConnectionError),
    before_sleep=before_sleep_log(logger, logging.WARNING),
    reraise=True
)

# Retry for cache operations
retry_cache = retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=0.5, min=0.5, max=5),
    retry=retry_if_exception_type(CacheConnectionError),
    before_sleep=before_sleep_log(logger, logging.WARNING),
    reraise=True
)

# Retry for external service calls
retry_external_service = retry(
    stop=stop_after_attempt(4),
    wait=wait_exponential(multiplier=2, min=2, max=16),
    retry=retry_if_exception_type(ExternalServiceError),
    before_sleep=before_sleep_log(logger, logging.WARNING),
    reraise=True
)


# ============================================================================
# Health Check Monitoring
# ============================================================================

class HealthMonitor:
    """Monitor health of services with circuit breakers."""

    def __init__(self):
        self.services: Dict[str, CircuitBreaker] = {}
        self.logger = logging.getLogger(__name__)

    def register_service(
        self,
        name: str,
        health_check_func: Callable,
        failure_threshold: int = 3,
        timeout_duration: int = 60
    ):
        """Register a service for health monitoring."""
        breaker = CircuitBreaker(
            name=f"health_{name}",
            failure_threshold=failure_threshold,
            timeout_duration=timeout_duration
        )
        self.services[name] = breaker
        self.logger.info(f"Registered health monitoring for service: {name}")

    async def check_health(self, service_name: str) -> bool:
        """Check health of a specific service."""
        if service_name not in self.services:
            raise ValueError(f"Service {service_name} not registered")

        breaker = self.services[service_name]

        # If circuit is open, service is unhealthy
        if breaker.state == CircuitState.OPEN:
            return False

        return True

    def get_all_health_status(self) -> Dict[str, Dict[str, Any]]:
        """Get health status of all services."""
        return {
            name: {
                "healthy": breaker.state != CircuitState.OPEN,
                "metrics": breaker.get_metrics()
            }
            for name, breaker in self.services.items()
        }


# Global health monitor instance
health_monitor = HealthMonitor()
