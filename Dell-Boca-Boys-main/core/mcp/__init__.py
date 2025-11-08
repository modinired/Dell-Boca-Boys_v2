"""
Multi-Component Platform (MCP)
==============================

The MCP provides a modular architecture for AI orchestration with the following components:

- **knowledge**: Evidence retrieval and knowledge grounding
- **triangulator**: Multi-model routing, adjudication, and self-checking
- **policy**: PII detection, redaction, and enforcement
- **codeexec**: Sandboxed code execution
- **workflow**: Declarative workflow orchestration
- **cards**: Predefined workflow templates
- **cli_agent**: CLI automation tools

This implementation follows the CESAR-SRC (Symbiotic Recursive Cognition) pattern
for enterprise-grade AI automation with governance and security built-in.
"""

__version__ = "1.0.0"

from . import knowledge
from . import triangulator
from . import policy
from . import codeexec
from . import workflow
from . import cards

__all__ = [
    "knowledge",
    "triangulator",
    "policy",
    "codeexec",
    "workflow",
    "cards",
]
