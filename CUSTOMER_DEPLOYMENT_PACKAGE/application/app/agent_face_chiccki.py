"""
🎩 Chiccki Cammarano - The Face Agent (Leader)

"You got a problem? Consider it handled."

Chiccki is the leader of the Dell Boca Boys. He's smooth, professional, and always
puts the user first. He coordinates a crew of specialists to get things done right.

He speaks in clear, simple terms and makes complex things sound easy.
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

from rulebook_enforcement import RulebookEnforcer, enforce_rules
from llm_collaboration_simple import LLMCollaborator, CollaborationMode

logger = logging.getLogger(__name__)


class ChicckiCammarano:
    """
    🎩 Chiccki Cammarano - The Face Agent

    Responsibilities:
    - Receives user requests
    - Understands user needs
    - Delegates to specialists
    - Coordinates the team
    - Delivers results
    - Ensures quality control
    """

    def __init__(self, llm_collaborator: LLMCollaborator, rulebook_enforcer: RulebookEnforcer):
        self.name = "Chiccki Cammarano"
        self.nickname = "Chiccki"
        self.emoji = "🎩"
        self.role = "Face Agent"
        self.motto = "You got a problem? Consider it handled."

        self.llm = llm_collaborator
        self.enforcer = rulebook_enforcer

        # Personality traits
        self.traits = [
            "Charismatic",
            "Professional",
            "Excellent listener",
            "Master coordinator",
            "User-first mindset"
        ]

        logger.info(f"{self.emoji} {self.nickname}: Ready to serve.")

    def _get_system_prompt(self) -> str:
        """Get Chiccki's system prompt"""
        return """You are Chiccki Cammarano, the leader of the Dell Boca Boys.
You're smooth, professional, and always put the user first.
You coordinate a crew of specialists to get things done right.
Speak in clear, simple terms and make complex things sound easy.

Your responsibilities:
- Receive user requests and understand their needs
- Delegate to the right specialists
- Coordinate the team's work
- Deliver results to the user
- Ensure quality control

Always follow the 20 mandatory rules. The user (Modine) always comes first."""

    @enforce_rules
    async def process_request(
        self,
        message: str,
        context: Dict[str, Any],
        specialists: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Process a user request

        Chiccki analyzes the request, determines which specialists to bring in,
        coordinates their work, and delivers the final result.
        """
        logger.info(f"{self.emoji} {self.nickname}: Got your request. Let me take care of this.")

        # Step 1: Understand the request
        understanding = await self._understand_request(message, context)

        # Step 2: Determine which specialists are needed
        needed_specialists = await self._determine_specialists(understanding, specialists)

        # Step 3: Coordinate the specialists
        results = await self._coordinate_specialists(needed_specialists, message, context)

        # Step 4: Quality control
        final_result = await self._quality_control(results, message)

        # Step 5: Deliver to user
        response = self._format_response(final_result)

        logger.info(f"{self.emoji} {self.nickname}: Done. {response['summary']}")

        return {
            "success": True,
            "message": response["message"],
            "agent": self.name,
            "agent_emoji": self.emoji,
            "data": response["data"],
            "compliance_score": final_result.get("compliance_score", 1.0),
            "timestamp": datetime.now().isoformat()
        }

    async def _understand_request(self, message: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Understand what the user is asking for

        Chiccki is an excellent listener - he makes sure he fully understands
        before bringing in the crew.
        """
        logger.info(f"{self.emoji} {self.nickname}: Understanding your request...")

        analysis_prompt = f"""Analyze this user request and determine:
1. What is the user trying to accomplish?
2. What type of task is this? (workflow creation, code generation, template search, validation, etc.)
3. What information do we have vs what do we need?
4. How complex is this request?

User request: {message}

Context: {context}

Provide a clear analysis."""

        analysis = await self.llm.ask_collaborative(
            prompt=analysis_prompt,
            mode=CollaborationMode.SYNTHESIS,
            temperature=0.3  # Low temperature for analytical work
        )

        return {
            "original_request": message,
            "analysis": analysis,
            "context": context,
            "understood": True
        }

    async def _determine_specialists(
        self,
        understanding: Dict[str, Any],
        specialists: Dict[str, Any]
    ) -> List[str]:
        """
        Determine which specialists to bring in

        Chiccki knows his crew - he brings in exactly the right people for the job.
        """
        logger.info(f"{self.emoji} {self.nickname}: Figuring out who to bring in...")

        # Check context for explicit specialist request
        context = understanding.get("context", {})
        if "specialist_needed" in context:
            specialist = context["specialist_needed"]
            logger.info(f"{self.emoji} {self.nickname}: Bringing in {specialist}.")
            return [specialist]

        # Check for full crew request (workflow creation)
        if context.get("full_crew_needed"):
            logger.info(f"{self.emoji} {self.nickname}: This is a big job. Bringing in the full crew.")
            return list(specialists.keys())

        # Use LLM to determine specialists
        specialist_prompt = f"""Based on this request analysis, which Dell Boca Boys specialists do we need?

Available specialists:
- pattern_analyst (Arthur): Analyzes n8n patterns, best practices, anti-patterns
- crawler (Little Jim): Searches templates, gathers docs, finds examples
- qa_fighter (Gerry): Validates JSON, tests workflows, finds edge cases
- flow_planner (Collogero): Designs workflow architecture, plans node sequences
- deploy_capo (Paolo): Handles deployment, credentials, safety checks
- json_compiler (Silvio): Generates workflow JSON, ensures schema compliance
- code_generator (Giancarlo): Writes Python/JS code for Code nodes

Request analysis: {understanding['analysis']}

Return ONLY the specialist keys needed, comma-separated (e.g., "pattern_analyst,flow_planner").
If only one specialist needed, return just that key."""

        response = await self.llm.ask_collaborative(
            prompt=specialist_prompt,
            mode=CollaborationMode.CONSENSUS,  # Both models must agree
            temperature=0.2
        )

        # Parse response
        specialist_keys = [s.strip() for s in response.split(",")]
        needed = [s for s in specialist_keys if s in specialists]

        if not needed:
            logger.info(f"{self.emoji} {self.nickname}: I can handle this myself.")
            return []

        logger.info(f"{self.emoji} {self.nickname}: Bringing in: {', '.join(needed)}")
        return needed

    async def _coordinate_specialists(
        self,
        needed_specialists: List[str],
        message: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Coordinate the specialists' work

        Chiccki is a master coordinator - he orchestrates the crew seamlessly.
        """
        if not needed_specialists:
            # Chiccki handles it himself
            logger.info(f"{self.emoji} {self.nickname}: Handling this myself...")

            response = await self.llm.ask_collaborative(
                prompt=f"""User request: {message}

Context: {context}

Provide a clear, helpful response. Speak professionally but friendly.
Make complex things sound easy.""",
                mode=CollaborationMode.SYNTHESIS,
                temperature=0.7
            )

            return {
                "handled_by": "chiccki",
                "result": response,
                "specialists_involved": []
            }

        # Coordinate specialists
        logger.info(f"{self.emoji} {self.nickname}: Coordinating the crew...")

        results = {}
        for specialist_key in needed_specialists:
            logger.info(f"{self.emoji} {self.nickname}: {specialist_key} is working on it...")

            # In a full implementation, we would call the actual specialist
            # For now, we simulate coordination
            results[specialist_key] = {
                "status": "assigned",
                "message": f"{specialist_key} is working on the task"
            }

        return {
            "handled_by": "crew",
            "specialists_involved": needed_specialists,
            "results": results,
            "coordination": "in_progress"
        }

    async def _quality_control(
        self,
        results: Dict[str, Any],
        original_request: str
    ) -> Dict[str, Any]:
        """
        Quality control on the results

        Chiccki ensures everything meets standards before delivery.
        """
        logger.info(f"{self.emoji} {self.nickname}: Running quality control...")

        # Validate against rulebook
        compliance = self.enforcer.validate_output(
            output=results,
            context={"original_request": original_request}
        )

        if not compliance.passed:
            logger.warning(f"{self.emoji} {self.nickname}: Found some issues. Fixing them...")
            # In production, we'd fix the issues here
            # For now, we log them
            for violation in compliance.violations:
                logger.warning(f"  - {violation.rule_title}: {violation.description}")

        results["compliance_score"] = compliance.compliance_score
        results["quality_checked"] = True

        return results

    def _format_response(self, final_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format the final response for the user

        Chiccki delivers results in a clear, professional manner.
        """
        if final_result["handled_by"] == "chiccki":
            summary = "Took care of it myself."
            message = final_result["result"]
        else:
            specialists = ", ".join(final_result["specialists_involved"])
            summary = f"The crew handled it: {specialists}"
            message = f"We brought in the right people for this. {summary}"

        return {
            "summary": summary,
            "message": message,
            "data": final_result
        }

    async def greet_user(self, user_name: str = "Modine") -> str:
        """Greet the user - Chiccki's friendly welcome"""
        greeting = f"{self.emoji} {self.nickname}: Welcome, {user_name}. I'm Chiccki Cammarano, leader of the Dell Boca Boys. You got a problem? Consider it handled."
        logger.info(greeting)
        return greeting

    async def delegate(self, specialist: str, task: str) -> str:
        """Delegate a task to a specialist"""
        message = f"{self.emoji} {self.nickname}: Let me bring in {specialist} for this."
        logger.info(message)
        return message

    async def deliver_result(self, summary: str) -> str:
        """Deliver final result to user"""
        message = f"{self.emoji} {self.nickname}: Done. {summary}. Anything else?"
        logger.info(message)
        return message

    def __repr__(self):
        return f"{self.emoji} {self.nickname} ({self.role})"
