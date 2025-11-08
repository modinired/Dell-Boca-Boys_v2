"""
Custom exception hierarchy for Dell Boca Boys V2.
Provides specific, actionable exceptions for all components.
"""
from typing import Optional, Dict, Any
from datetime import datetime


class DellBocaBoysException(Exception):
    """Base exception for all Dell Boca Boys errors."""

    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        recoverable: bool = False
    ):
        super().__init__(message)
        self.message = message
        self.error_code = error_code or self.__class__.__name__
        self.details = details or {}
        self.recoverable = recoverable
        self.timestamp = datetime.utcnow()

    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary for logging/API responses."""
        return {
            "error_type": self.__class__.__name__,
            "error_code": self.error_code,
            "message": self.message,
            "details": self.details,
            "recoverable": self.recoverable,
            "timestamp": self.timestamp.isoformat()
        }


# ============================================================================
# Agent Exceptions
# ============================================================================

class AgentException(DellBocaBoysException):
    """Base exception for agent-related errors."""
    pass


class AgentNotFoundError(AgentException):
    """Raised when an agent cannot be found."""

    def __init__(self, agent_id: str, **kwargs):
        super().__init__(
            message=f"Agent not found: {agent_id}",
            error_code="AGENT_NOT_FOUND",
            details={"agent_id": agent_id},
            **kwargs
        )


class AgentInitializationError(AgentException):
    """Raised when agent initialization fails."""

    def __init__(self, agent_id: str, reason: str, **kwargs):
        super().__init__(
            message=f"Failed to initialize agent {agent_id}: {reason}",
            error_code="AGENT_INIT_FAILED",
            details={"agent_id": agent_id, "reason": reason},
            recoverable=True,
            **kwargs
        )


class AgentCommunicationError(AgentException):
    """Raised when agent communication fails."""

    def __init__(self, source_agent: str, target_agent: str, reason: str, **kwargs):
        super().__init__(
            message=f"Communication failed from {source_agent} to {target_agent}: {reason}",
            error_code="AGENT_COMM_FAILED",
            details={
                "source_agent": source_agent,
                "target_agent": target_agent,
                "reason": reason
            },
            recoverable=True,
            **kwargs
        )


class AgentHealthCheckError(AgentException):
    """Raised when agent health check fails."""

    def __init__(self, agent_id: str, health_status: Dict[str, Any], **kwargs):
        super().__init__(
            message=f"Agent {agent_id} health check failed",
            error_code="AGENT_UNHEALTHY",
            details={"agent_id": agent_id, "health_status": health_status},
            recoverable=True,
            **kwargs
        )


class AgentCapacityExceededError(AgentException):
    """Raised when agent capacity is exceeded."""

    def __init__(self, agent_id: str, current_load: int, max_capacity: int, **kwargs):
        super().__init__(
            message=f"Agent {agent_id} capacity exceeded: {current_load}/{max_capacity}",
            error_code="AGENT_CAPACITY_EXCEEDED",
            details={
                "agent_id": agent_id,
                "current_load": current_load,
                "max_capacity": max_capacity
            },
            recoverable=True,
            **kwargs
        )


# ============================================================================
# Memory Exceptions
# ============================================================================

class MemoryException(DellBocaBoysException):
    """Base exception for memory-related errors."""
    pass


class MemoryProviderError(MemoryException):
    """Raised when memory provider operation fails."""

    def __init__(self, provider: str, operation: str, reason: str, **kwargs):
        super().__init__(
            message=f"Memory provider {provider} failed during {operation}: {reason}",
            error_code="MEMORY_PROVIDER_ERROR",
            details={"provider": provider, "operation": operation, "reason": reason},
            recoverable=True,
            **kwargs
        )


class MemoryNotFoundError(MemoryException):
    """Raised when memory entry cannot be found."""

    def __init__(self, memory_id: str, **kwargs):
        super().__init__(
            message=f"Memory not found: {memory_id}",
            error_code="MEMORY_NOT_FOUND",
            details={"memory_id": memory_id},
            **kwargs
        )


class MemoryStorageError(MemoryException):
    """Raised when memory storage fails."""

    def __init__(self, reason: str, memory_type: Optional[str] = None, **kwargs):
        super().__init__(
            message=f"Failed to store memory: {reason}",
            error_code="MEMORY_STORAGE_FAILED",
            details={"reason": reason, "memory_type": memory_type},
            recoverable=True,
            **kwargs
        )


class MemoryRetrievalError(MemoryException):
    """Raised when memory retrieval fails."""

    def __init__(self, reason: str, query: Optional[Dict[str, Any]] = None, **kwargs):
        super().__init__(
            message=f"Failed to retrieve memory: {reason}",
            error_code="MEMORY_RETRIEVAL_FAILED",
            details={"reason": reason, "query": query},
            recoverable=True,
            **kwargs
        )


class MemoryQuotaExceededError(MemoryException):
    """Raised when memory quota is exceeded."""

    def __init__(self, current_size: int, max_size: int, **kwargs):
        super().__init__(
            message=f"Memory quota exceeded: {current_size}/{max_size} bytes",
            error_code="MEMORY_QUOTA_EXCEEDED",
            details={"current_size": current_size, "max_size": max_size},
            **kwargs
        )


# ============================================================================
# LLM Exceptions
# ============================================================================

class LLMException(DellBocaBoysException):
    """Base exception for LLM-related errors."""
    pass


class LLMProviderError(LLMException):
    """Raised when LLM provider fails."""

    def __init__(self, provider: str, model: str, reason: str, **kwargs):
        super().__init__(
            message=f"LLM provider {provider} (model: {model}) failed: {reason}",
            error_code="LLM_PROVIDER_ERROR",
            details={"provider": provider, "model": model, "reason": reason},
            recoverable=True,
            **kwargs
        )


class LLMTimeoutError(LLMException):
    """Raised when LLM request times out."""

    def __init__(self, provider: str, timeout_seconds: int, **kwargs):
        super().__init__(
            message=f"LLM request to {provider} timed out after {timeout_seconds}s",
            error_code="LLM_TIMEOUT",
            details={"provider": provider, "timeout_seconds": timeout_seconds},
            recoverable=True,
            **kwargs
        )


class LLMRateLimitError(LLMException):
    """Raised when LLM rate limit is exceeded."""

    def __init__(self, provider: str, retry_after: Optional[int] = None, **kwargs):
        super().__init__(
            message=f"LLM rate limit exceeded for {provider}",
            error_code="LLM_RATE_LIMIT",
            details={"provider": provider, "retry_after": retry_after},
            recoverable=True,
            **kwargs
        )


class LLMResponseValidationError(LLMException):
    """Raised when LLM response validation fails."""

    def __init__(self, reason: str, response_snippet: Optional[str] = None, **kwargs):
        super().__init__(
            message=f"LLM response validation failed: {reason}",
            error_code="LLM_INVALID_RESPONSE",
            details={"reason": reason, "response_snippet": response_snippet},
            recoverable=True,
            **kwargs
        )


# ============================================================================
# Workflow Exceptions
# ============================================================================

class WorkflowException(DellBocaBoysException):
    """Base exception for workflow-related errors."""
    pass


class WorkflowValidationError(WorkflowException):
    """Raised when workflow validation fails."""

    def __init__(self, workflow_id: str, validation_errors: list, **kwargs):
        super().__init__(
            message=f"Workflow {workflow_id} validation failed",
            error_code="WORKFLOW_INVALID",
            details={"workflow_id": workflow_id, "validation_errors": validation_errors},
            **kwargs
        )


class WorkflowExecutionError(WorkflowException):
    """Raised when workflow execution fails."""

    def __init__(self, workflow_id: str, execution_id: str, reason: str, **kwargs):
        super().__init__(
            message=f"Workflow {workflow_id} execution {execution_id} failed: {reason}",
            error_code="WORKFLOW_EXEC_FAILED",
            details={
                "workflow_id": workflow_id,
                "execution_id": execution_id,
                "reason": reason
            },
            recoverable=True,
            **kwargs
        )


class WorkflowNotFoundError(WorkflowException):
    """Raised when workflow cannot be found."""

    def __init__(self, workflow_id: str, **kwargs):
        super().__init__(
            message=f"Workflow not found: {workflow_id}",
            error_code="WORKFLOW_NOT_FOUND",
            details={"workflow_id": workflow_id},
            **kwargs
        )


class WorkflowDeploymentError(WorkflowException):
    """Raised when workflow deployment fails."""

    def __init__(self, workflow_id: str, target: str, reason: str, **kwargs):
        super().__init__(
            message=f"Failed to deploy workflow {workflow_id} to {target}: {reason}",
            error_code="WORKFLOW_DEPLOY_FAILED",
            details={"workflow_id": workflow_id, "target": target, "reason": reason},
            recoverable=True,
            **kwargs
        )


# ============================================================================
# Database Exceptions
# ============================================================================

class DatabaseException(DellBocaBoysException):
    """Base exception for database-related errors."""
    pass


class DatabaseConnectionError(DatabaseException):
    """Raised when database connection fails."""

    def __init__(self, database: str, reason: str, **kwargs):
        super().__init__(
            message=f"Failed to connect to database {database}: {reason}",
            error_code="DB_CONNECTION_FAILED",
            details={"database": database, "reason": reason},
            recoverable=True,
            **kwargs
        )


class DatabaseQueryError(DatabaseException):
    """Raised when database query fails."""

    def __init__(self, query_type: str, reason: str, **kwargs):
        super().__init__(
            message=f"Database {query_type} query failed: {reason}",
            error_code="DB_QUERY_FAILED",
            details={"query_type": query_type, "reason": reason},
            recoverable=True,
            **kwargs
        )


class DatabaseIntegrityError(DatabaseException):
    """Raised when database integrity constraint is violated."""

    def __init__(self, constraint: str, details: str, **kwargs):
        super().__init__(
            message=f"Database integrity violation on {constraint}: {details}",
            error_code="DB_INTEGRITY_ERROR",
            details={"constraint": constraint, "details": details},
            **kwargs
        )


# ============================================================================
# Cache Exceptions
# ============================================================================

class CacheException(DellBocaBoysException):
    """Base exception for cache-related errors."""
    pass


class CacheConnectionError(CacheException):
    """Raised when cache connection fails."""

    def __init__(self, cache_type: str, reason: str, **kwargs):
        super().__init__(
            message=f"Failed to connect to {cache_type} cache: {reason}",
            error_code="CACHE_CONNECTION_FAILED",
            details={"cache_type": cache_type, "reason": reason},
            recoverable=True,
            **kwargs
        )


class CacheOperationError(CacheException):
    """Raised when cache operation fails."""

    def __init__(self, operation: str, namespace: str, reason: str, **kwargs):
        super().__init__(
            message=f"Cache {operation} failed for namespace {namespace}: {reason}",
            error_code="CACHE_OPERATION_FAILED",
            details={"operation": operation, "namespace": namespace, "reason": reason},
            recoverable=True,
            **kwargs
        )


# ============================================================================
# API Exceptions
# ============================================================================

class APIException(DellBocaBoysException):
    """Base exception for API-related errors."""
    pass


class AuthenticationError(APIException):
    """Raised when authentication fails."""

    def __init__(self, reason: str, **kwargs):
        super().__init__(
            message=f"Authentication failed: {reason}",
            error_code="AUTH_FAILED",
            details={"reason": reason},
            **kwargs
        )


class AuthorizationError(APIException):
    """Raised when authorization fails."""

    def __init__(self, user_id: str, resource: str, action: str, **kwargs):
        super().__init__(
            message=f"User {user_id} not authorized for {action} on {resource}",
            error_code="AUTH_DENIED",
            details={"user_id": user_id, "resource": resource, "action": action},
            **kwargs
        )


class RateLimitExceededError(APIException):
    """Raised when API rate limit is exceeded."""

    def __init__(self, endpoint: str, limit: int, window: int, **kwargs):
        super().__init__(
            message=f"Rate limit exceeded for {endpoint}: {limit} requests per {window}s",
            error_code="RATE_LIMIT_EXCEEDED",
            details={"endpoint": endpoint, "limit": limit, "window": window},
            recoverable=True,
            **kwargs
        )


class InvalidRequestError(APIException):
    """Raised when API request is invalid."""

    def __init__(self, reason: str, validation_errors: Optional[list] = None, **kwargs):
        super().__init__(
            message=f"Invalid request: {reason}",
            error_code="INVALID_REQUEST",
            details={"reason": reason, "validation_errors": validation_errors},
            **kwargs
        )


# ============================================================================
# Integration Exceptions
# ============================================================================

class IntegrationException(DellBocaBoysException):
    """Base exception for external integration errors."""
    pass


class N8NIntegrationError(IntegrationException):
    """Raised when n8n integration fails."""

    def __init__(self, operation: str, reason: str, **kwargs):
        super().__init__(
            message=f"n8n {operation} failed: {reason}",
            error_code="N8N_INTEGRATION_ERROR",
            details={"operation": operation, "reason": reason},
            recoverable=True,
            **kwargs
        )


class ExternalServiceError(IntegrationException):
    """Raised when external service call fails."""

    def __init__(self, service: str, endpoint: str, status_code: int, reason: str, **kwargs):
        super().__init__(
            message=f"External service {service} ({endpoint}) failed with status {status_code}: {reason}",
            error_code="EXTERNAL_SERVICE_ERROR",
            details={
                "service": service,
                "endpoint": endpoint,
                "status_code": status_code,
                "reason": reason
            },
            recoverable=True,
            **kwargs
        )


# ============================================================================
# Configuration Exceptions
# ============================================================================

class ConfigurationException(DellBocaBoysException):
    """Base exception for configuration errors."""
    pass


class MissingConfigurationError(ConfigurationException):
    """Raised when required configuration is missing."""

    def __init__(self, config_key: str, **kwargs):
        super().__init__(
            message=f"Required configuration missing: {config_key}",
            error_code="CONFIG_MISSING",
            details={"config_key": config_key},
            **kwargs
        )


class InvalidConfigurationError(ConfigurationException):
    """Raised when configuration is invalid."""

    def __init__(self, config_key: str, reason: str, **kwargs):
        super().__init__(
            message=f"Invalid configuration for {config_key}: {reason}",
            error_code="CONFIG_INVALID",
            details={"config_key": config_key, "reason": reason},
            **kwargs
        )
