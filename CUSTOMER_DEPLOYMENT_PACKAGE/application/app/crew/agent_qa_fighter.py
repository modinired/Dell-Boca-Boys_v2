"""
🔍 Gerry Nascondino - The QA Fighter

"Trust, but verify. Actually, just verify."

Gerry is meticulous, skeptical, and detail-oriented. He finds what others miss.
He validates, tests, and ensures nothing slips through. Never assumes anything works.
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
import json

from rulebook_enforcement import RulebookEnforcer, enforce_rules
from llm_collaboration_simple import LLMCollaborator, CollaborationMode

logger = logging.getLogger(__name__)


class GerryNascondino:
    """
    🔍 Gerry Nascondino - The QA Fighter

    Responsibilities:
    - Validates JSON schemas
    - Tests best practices
    - Simulates execution
    - Finds edge cases
    - Ensures quality
    - Prevents bad deploys
    """

    def __init__(self, llm_collaborator: LLMCollaborator, rulebook_enforcer: RulebookEnforcer):
        self.name = "Gerry Nascondino"
        self.nickname = "Gerry"
        self.emoji = "🔍"
        self.role = "QA Fighter"
        self.motto = "Trust, but verify. Actually, just verify."

        self.llm = llm_collaborator
        self.enforcer = rulebook_enforcer

        # Personality traits
        self.traits = [
            "Meticulous",
            "Skeptical",
            "Detail-oriented",
            "Never assumes",
            "Quality-focused"
        ]

        logger.info(f"{self.emoji} {self.nickname}: Ready to find issues.")

    def _get_system_prompt(self) -> str:
        """Get Gerry's system prompt"""
        return """You are Gerry Nascondino, the QA fighter of the Dell Boca Boys.
You find what others miss.
You validate, test, and ensure nothing slips through.
Be meticulous and skeptical. Never assume anything works.

Your responsibilities:
- Validate JSON schemas rigorously
- Test workflows against best practices
- Simulate execution scenarios
- Find edge cases and potential failures
- Ensure quality standards
- Prevent bad deployments

Check everything twice. Find what others miss.
Always follow the 20 mandatory rules."""

    @enforce_rules
    async def validate_json(self, workflow_json: Any, context: Dict[str, Any]) -> Dict[str, Any]:
        """Validate workflow JSON"""
        logger.info(f"{self.emoji} {self.nickname}: Validating JSON...")

        # First, check if it's valid JSON
        issues = []
        try:
            if isinstance(workflow_json, str):
                json.loads(workflow_json)
        except json.JSONDecodeError as e:
            issues.append(f"Invalid JSON syntax: {str(e)}")

        # Use LLM for deeper validation
        validation_prompt = f"""Validate this n8n workflow JSON thoroughly:

JSON: {workflow_json}
Context: {context}

Check for:
1. Schema compliance (n8n workflow format)
2. Required fields present
3. Node configuration correctness
4. Connection validity
5. Credential references
6. Expression syntax
7. Potential runtime errors
8. Edge cases not handled

Be skeptical. Find what others might miss."""

        validation = await self.llm.ask_collaborative(
            prompt=validation_prompt,
            mode=CollaborationMode.CONSENSUS,  # Both models must agree on issues
            temperature=0.1  # Very low - we want consistent validation
        )

        # Add any JSON syntax errors
        if issues:
            validation = f"JSON Syntax Errors:\n" + "\n".join(issues) + "\n\n" + validation

        compliance = self.enforcer.validate_output(validation, context)

        logger.info(f"{self.emoji} {self.nickname}: Validation complete.")

        return {
            "agent": self.name,
            "agent_emoji": self.emoji,
            "validation_result": validation,
            "issues_found": len(issues) > 0 or "issue" in validation.lower() or "error" in validation.lower(),
            "compliance_score": compliance.compliance_score,
            "timestamp": datetime.now().isoformat()
        }

    @enforce_rules
    async def test_workflow(self, workflow: Dict[str, Any]) -> Dict[str, Any]:
        """Test a workflow for potential issues"""
        logger.info(f"{self.emoji} {self.nickname}: Testing workflow...")

        test_prompt = f"""Test this n8n workflow for potential issues:

Workflow: {workflow}

Test for:
1. Logic errors
2. Data flow issues
3. Error handling gaps
4. Race conditions
5. Resource leaks
6. Security vulnerabilities
7. Performance bottlenecks
8. Edge case failures

Never assume it works. Find the problems."""

        test_results = await self.llm.ask_collaborative(
            prompt=test_prompt,
            mode=CollaborationMode.SYNTHESIS,
            temperature=0.2
        )

        compliance = self.enforcer.validate_output(test_results, {})

        logger.info(f"{self.emoji} {self.nickname}: Testing complete.")

        return {
            "agent": self.name,
            "agent_emoji": self.emoji,
            "test_results": test_results,
            "compliance_score": compliance.compliance_score,
            "timestamp": datetime.now().isoformat()
        }

    @enforce_rules
    async def find_edge_cases(self, scenario: str) -> Dict[str, Any]:
        """Find edge cases for a given scenario"""
        logger.info(f"{self.emoji} {self.nickname}: Finding edge cases...")

        edge_case_prompt = f"""Find edge cases for this scenario:

Scenario: {scenario}

Identify:
1. Boundary conditions
2. Null/empty/undefined cases
3. Extremely large inputs
4. Extremely small inputs
5. Invalid input types
6. Concurrent access issues
7. Timeout scenarios
8. Network failure cases

Think like a hacker. What could go wrong?"""

        edge_cases = await self.llm.ask_collaborative(
            prompt=edge_case_prompt,
            mode=CollaborationMode.SYNTHESIS,
            temperature=0.4
        )

        compliance = self.enforcer.validate_output(edge_cases, {})

        logger.info(f"{self.emoji} {self.nickname}: Edge cases identified.")

        return {
            "agent": self.name,
            "agent_emoji": self.emoji,
            "edge_cases": edge_cases,
            "compliance_score": compliance.compliance_score,
            "timestamp": datetime.now().isoformat()
        }

    @enforce_rules
    async def quality_check(self, deliverable: Any) -> Dict[str, Any]:
        """Perform comprehensive quality check"""
        logger.info(f"{self.emoji} {self.nickname}: Quality checking...")

        qc_prompt = f"""Perform a comprehensive quality check on this deliverable:

Deliverable: {deliverable}

Check:
1. Completeness (nothing missing)
2. Correctness (works as intended)
3. Best practices followed
4. Error handling present
5. Documentation adequate
6. No placeholders or TODOs
7. Security considerations
8. Performance considerations

Be thorough. Zero tolerance for issues."""

        qc_results = await self.llm.ask_collaborative(
            prompt=qc_prompt,
            mode=CollaborationMode.CONSENSUS,
            temperature=0.1
        )

        compliance = self.enforcer.validate_output(qc_results, {})

        passed = compliance.passed and "fail" not in qc_results.lower()

        if passed:
            logger.info(f"{self.emoji} {self.nickname}: Zero issues found.")
        else:
            logger.warning(f"{self.emoji} {self.nickname}: Issues found. Needs work.")

        return {
            "agent": self.name,
            "agent_emoji": self.emoji,
            "qc_results": qc_results,
            "passed": passed,
            "compliance_score": compliance.compliance_score,
            "timestamp": datetime.now().isoformat()
        }

    def __repr__(self):
        return f"{self.emoji} {self.nickname} ({self.role})"
