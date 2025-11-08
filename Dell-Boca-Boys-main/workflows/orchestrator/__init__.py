"""
Workflow Orchestrator for Dell-Boca-Boys Enterprise Integration
===============================================================

Complete RWCM (Role-Workflow-Capability-Mapping) orchestrator with:
- Schema registry and validation
- Secrets management (Vault + local)
- Enterprise adapters (AWS, SAP, Okta, Workday)
- HMAC security
- Governance framework
- Event bus integration
"""

__version__ = "1.1.0"

from .runtime import OrchestratorRuntime
from .registry import SchemaRegistry
from .secrets import SecretProvider
from .models import (
    ExecuteWorkflow,
    ExecuteStep,
    Reflection,
    Workflow,
    StepAction,
    RunEpisode,
    StepRun
)

__all__ = [
    "OrchestratorRuntime",
    "SchemaRegistry",
    "SecretProvider",
    "ExecuteWorkflow",
    "ExecuteStep",
    "Reflection",
    "Workflow",
    "StepAction",
    "RunEpisode",
    "StepRun",
]
