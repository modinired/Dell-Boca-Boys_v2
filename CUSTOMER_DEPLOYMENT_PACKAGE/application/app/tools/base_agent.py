"""
Base Agent Class

All Dell Boca Boys agents can inherit from this base class
for common functionality.
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime
from abc import ABC, abstractmethod

from rulebook_enforcement import RulebookEnforcer
from llm_collaboration_simple import LLMCollaborator

logger = logging.getLogger(__name__)


class BaseAgent(ABC):
    """
    Base class for all Dell Boca Boys agents

    Provides common functionality:
    - Logging with emoji
    - LLM collaboration
    - Rulebook enforcement
    - Response formatting
    """

    def __init__(
        self,
        name: str,
        nickname: str,
        emoji: str,
        role: str,
        motto: str,
        traits: list,
        llm_collaborator: LLMCollaborator,
        rulebook_enforcer: RulebookEnforcer
    ):
        self.name = name
        self.nickname = nickname
        self.emoji = emoji
        self.role = role
        self.motto = motto
        self.traits = traits

        self.llm = llm_collaborator
        self.enforcer = rulebook_enforcer

        logger.info(f"{self.emoji} {self.nickname}: Initialized and ready.")

    @abstractmethod
    def _get_system_prompt(self) -> str:
        """Get the agent's system prompt - must be implemented by subclasses"""
        pass

    def log(self, message: str, level: str = "info"):
        """Log a message with the agent's emoji"""
        log_message = f"{self.emoji} {self.nickname}: {message}"

        if level == "info":
            logger.info(log_message)
        elif level == "warning":
            logger.warning(log_message)
        elif level == "error":
            logger.error(log_message)
        elif level == "debug":
            logger.debug(log_message)

    def format_response(
        self,
        data: Any,
        message: Optional[str] = None,
        compliance_score: float = 1.0
    ) -> Dict[str, Any]:
        """Format a standard response"""
        return {
            "agent": self.name,
            "agent_emoji": self.emoji,
            "message": message or f"{self.nickname} completed the task",
            "data": data,
            "compliance_score": compliance_score,
            "timestamp": datetime.now().isoformat()
        }

    async def validate_with_rulebook(self, output: Any, context: Dict[str, Any]) -> float:
        """Validate output against rulebook and return compliance score"""
        compliance = self.enforcer.validate_output(output, context)

        if not compliance.passed:
            self.log(f"Rulebook violations detected: {len(compliance.violations)}", "warning")
            for violation in compliance.violations:
                self.log(f"  - Rule {violation.rule_id}: {violation.description}", "warning")

        return compliance.compliance_score

    def __repr__(self):
        return f"{self.emoji} {self.nickname} ({self.role})"

    def __str__(self):
        return f"{self.name} - {self.role}"
