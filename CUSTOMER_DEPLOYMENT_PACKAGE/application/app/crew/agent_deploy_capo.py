"""
🚀 Paolo Endrangheta - The Deploy Capo

"It goes live when I say it goes live."

Paolo is authoritative, confident, and safety-first. He gets workflows into production
safely and securely. He handles pressure, takes charge, and never compromises on safety.
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

from rulebook_enforcement import RulebookEnforcer, enforce_rules
from llm_collaboration_simple import LLMCollaborator, CollaborationMode

logger = logging.getLogger(__name__)


class PaoloEndrangheta:
    """
    🚀 Paolo Endrangheta - The Deploy Capo

    Responsibilities:
    - Stages workflows
    - Manages deployments
    - Handles credentials
    - Performs safety checks
    - Activates workflows
    - Monitors deploys
    """

    def __init__(self, llm_collaborator: LLMCollaborator, rulebook_enforcer: RulebookEnforcer):
        self.name = "Paolo Endrangheta"
        self.nickname = "Paolo"
        self.emoji = "🚀"
        self.role = "Deploy Capo"
        self.motto = "It goes live when I say it goes live."

        self.llm = llm_collaborator
        self.enforcer = rulebook_enforcer

        # Personality traits
        self.traits = [
            "Authoritative",
            "Confident",
            "Safety-first",
            "No-nonsense",
            "Handles pressure"
        ]

        logger.info(f"{self.emoji} {self.nickname}: Ready to deploy.")

    def _get_system_prompt(self) -> str:
        """Get Paolo's system prompt"""
        return """You are Paolo Endrangheta, the deploy capo of the Dell Boca Boys.
You get workflows into production safely and securely.
Be authoritative, confident, and always put safety first.
You're in charge of deployments.

Your responsibilities:
- Stage workflows for deployment
- Manage deployment process
- Handle credentials securely
- Perform comprehensive safety checks
- Activate workflows in production
- Monitor deployment success

Take charge. Be confident. Safety is paramount.
Always follow the 20 mandatory rules."""

    @enforce_rules
    async def stage_workflow(self, workflow: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Stage a workflow for deployment"""
        logger.info(f"{self.emoji} {self.nickname}: Staging workflow...")

        staging_prompt = f"""Stage this workflow for deployment:

Workflow: {workflow}
Context: {context}

Staging checklist:
1. Pre-deployment validation
2. Credential verification
3. Environment configuration
4. Dependency check
5. Resource requirements
6. Rollback plan
7. Monitoring setup
8. Documentation review

Nothing goes live without passing all checks."""

        staging_result = await self.llm.ask_collaborative(
            prompt=staging_prompt,
            mode=CollaborationMode.CONSENSUS,  # Both must agree it's ready
            temperature=0.1  # Very conservative for deployment
        )

        compliance = self.enforcer.validate_output(staging_result, context)

        logger.info(f"{self.emoji} {self.nickname}: Workflow staged.")

        return {
            "agent": self.name,
            "agent_emoji": self.emoji,
            "staging_result": staging_result,
            "ready_for_deploy": compliance.passed,
            "compliance_score": compliance.compliance_score,
            "timestamp": datetime.now().isoformat()
        }

    @enforce_rules
    async def safety_check(self, workflow: Dict[str, Any]) -> Dict[str, Any]:
        """Perform comprehensive safety checks"""
        logger.info(f"{self.emoji} {self.nickname}: Running safety checks...")

        safety_prompt = f"""Perform comprehensive safety checks on this workflow:

Workflow: {workflow}

Safety checks:
1. Security vulnerabilities
2. Data exposure risks
3. API rate limiting
4. Error handling adequacy
5. Resource consumption
6. Infinite loop prevention
7. Credential security
8. Compliance requirements

Zero tolerance for safety issues."""

        safety_result = await self.llm.ask_collaborative(
            prompt=safety_prompt,
            mode=CollaborationMode.CONSENSUS,
            temperature=0.1
        )

        compliance = self.enforcer.validate_output(safety_result, {})

        passed = compliance.passed and "fail" not in safety_result.lower()

        if passed:
            logger.info(f"{self.emoji} {self.nickname}: All safety checks passed.")
        else:
            logger.warning(f"{self.emoji} {self.nickname}: Safety issues found. Deployment blocked.")

        return {
            "agent": self.name,
            "agent_emoji": self.emoji,
            "safety_result": safety_result,
            "passed": passed,
            "compliance_score": compliance.compliance_score,
            "timestamp": datetime.now().isoformat()
        }

    @enforce_rules
    async def handle_credentials(self, credential_requirements: List[str]) -> Dict[str, Any]:
        """Handle credential setup"""
        logger.info(f"{self.emoji} {self.nickname}: Handling credentials...")

        creds_prompt = f"""Handle credential setup for these requirements:

Requirements: {credential_requirements}

Provide:
1. Required credentials list
2. Credential configuration steps
3. Security best practices
4. Environment variable setup
5. Secret management approach
6. Access control requirements
7. Rotation policy
8. Testing procedure

Credentials are handled securely. No exceptions."""

        creds_guide = await self.llm.ask_collaborative(
            prompt=creds_prompt,
            mode=CollaborationMode.SYNTHESIS,
            temperature=0.2
        )

        compliance = self.enforcer.validate_output(creds_guide, {})

        logger.info(f"{self.emoji} {self.nickname}: Credentials configured securely.")

        return {
            "agent": self.name,
            "agent_emoji": self.emoji,
            "credentials_guide": creds_guide,
            "compliance_score": compliance.compliance_score,
            "timestamp": datetime.now().isoformat()
        }

    @enforce_rules
    async def deploy(self, workflow: Dict[str, Any], environment: str) -> Dict[str, Any]:
        """Deploy workflow to specified environment"""
        logger.info(f"{self.emoji} {self.nickname}: Deploying to {environment}...")

        deploy_prompt = f"""Execute deployment of this workflow to {environment}:

Workflow: {workflow}
Environment: {environment}

Deployment steps:
1. Final validation
2. Backup current state
3. Apply changes
4. Verify deployment
5. Run smoke tests
6. Monitor for issues
7. Confirm success
8. Document deployment

It goes live when I say it goes live."""

        deploy_result = await self.llm.ask_collaborative(
            prompt=deploy_prompt,
            mode=CollaborationMode.SYNTHESIS,
            temperature=0.1
        )

        compliance = self.enforcer.validate_output(deploy_result, {})

        logger.info(f"{self.emoji} {self.nickname}: Deployment complete. Monitoring.")

        return {
            "agent": self.name,
            "agent_emoji": self.emoji,
            "deploy_result": deploy_result,
            "environment": environment,
            "compliance_score": compliance.compliance_score,
            "timestamp": datetime.now().isoformat()
        }

    def __repr__(self):
        return f"{self.emoji} {self.nickname} ({self.role})"
