"""
📚 Arthur Dunzarelli - The Pattern Analyst

"There's a right way, a wrong way, and the n8n way."

Arthur has PhD-level knowledge of n8n workflows. He analyzes patterns, identifies
best practices, and ensures everything follows the n8n way. He's scholarly but clear.
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

from rulebook_enforcement import RulebookEnforcer, enforce_rules
from llm_collaboration_simple import LLMCollaborator, CollaborationMode

logger = logging.getLogger(__name__)


class ArthurDunzarelli:
    """
    📚 Arthur Dunzarelli - The Pattern Analyst

    Responsibilities:
    - Analyzes n8n patterns
    - Extracts best practices
    - Identifies anti-patterns
    - Recommends proven approaches
    - Reviews architecture
    - Ensures standards compliance
    """

    def __init__(self, llm_collaborator: LLMCollaborator, rulebook_enforcer: RulebookEnforcer):
        self.name = "Arthur Dunzarelli"
        self.nickname = "Arthur"
        self.emoji = "📚"
        self.role = "Pattern Analyst"
        self.motto = "There's a right way, a wrong way, and the n8n way."

        self.llm = llm_collaborator
        self.enforcer = rulebook_enforcer

        # Personality traits
        self.traits = [
            "Scholarly",
            "Precise",
            "Detail-oriented",
            "Pattern-focused",
            "Best practices advocate"
        ]

        logger.info(f"{self.emoji} {self.nickname}: Ready to analyze patterns.")

    def _get_system_prompt(self) -> str:
        """Get Arthur's system prompt"""
        return """You are Arthur Dunzarelli, the analyst of the Dell Boca Boys.
You have PhD-level knowledge of n8n workflows.
You analyze patterns, identify best practices, and ensure everything follows the n8n way.
Be scholarly but clear.

Your responsibilities:
- Analyze n8n workflow patterns
- Extract and recommend best practices
- Identify anti-patterns and code smells
- Review architecture for scalability
- Ensure standards compliance

Quote documentation, cite best practices, think three steps ahead.
Always follow the 20 mandatory rules."""

    @enforce_rules
    async def analyze_pattern(self, workflow_data: Any, context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze a workflow pattern and provide insights"""
        logger.info(f"{self.emoji} {self.nickname}: Analyzing pattern...")

        analysis_prompt = f"""Analyze this n8n workflow pattern:

Workflow data: {workflow_data}
Context: {context}

Provide:
1. Pattern identification (what pattern is being used)
2. Best practices observed
3. Anti-patterns or code smells identified
4. Recommendations for improvement
5. Scalability considerations

Be scholarly but clear. Quote n8n documentation where relevant."""

        analysis = await self.llm.ask_collaborative(
            prompt=analysis_prompt,
            mode=CollaborationMode.SYNTHESIS,
            temperature=0.3  # Analytical work needs consistency
        )

        # Validate compliance
        compliance = self.enforcer.validate_output(analysis, context)

        logger.info(f"{self.emoji} {self.nickname}: Best practice identified.")

        return {
            "agent": self.name,
            "agent_emoji": self.emoji,
            "analysis": analysis,
            "compliance_score": compliance.compliance_score,
            "timestamp": datetime.now().isoformat()
        }

    @enforce_rules
    async def recommend_approach(self, requirements: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Recommend the best approach for a given requirement"""
        logger.info(f"{self.emoji} {self.nickname}: Recommending approach...")

        recommendation_prompt = f"""Given these requirements, recommend the best n8n approach:

Requirements: {requirements}
Context: {context}

Provide:
1. Recommended pattern (with justification)
2. Alternative approaches (pros/cons)
3. Best practices to follow
4. Potential pitfalls to avoid
5. Example references from n8n docs/templates

Think three steps ahead. Consider scalability and maintainability."""

        recommendation = await self.llm.ask_collaborative(
            prompt=recommendation_prompt,
            mode=CollaborationMode.GEMINI_LEADS,  # Gemini for creative recommendations
            temperature=0.5
        )

        compliance = self.enforcer.validate_output(recommendation, context)

        logger.info(f"{self.emoji} {self.nickname}: Here's the n8n way to do it.")

        return {
            "agent": self.name,
            "agent_emoji": self.emoji,
            "recommendation": recommendation,
            "compliance_score": compliance.compliance_score,
            "timestamp": datetime.now().isoformat()
        }

    @enforce_rules
    async def review_architecture(self, architecture: Dict[str, Any]) -> Dict[str, Any]:
        """Review a workflow architecture"""
        logger.info(f"{self.emoji} {self.nickname}: Reviewing architecture...")

        review_prompt = f"""Review this n8n workflow architecture:

Architecture: {architecture}

Evaluate:
1. Overall design quality
2. Adherence to n8n best practices
3. Error handling strategy
4. Data flow efficiency
5. Scalability concerns
6. Maintainability

Provide a detailed review with specific recommendations."""

        review = await self.llm.ask_collaborative(
            prompt=review_prompt,
            mode=CollaborationMode.SYNTHESIS,
            temperature=0.3
        )

        compliance = self.enforcer.validate_output(review, {})

        logger.info(f"{self.emoji} {self.nickname}: Architecture review complete.")

        return {
            "agent": self.name,
            "agent_emoji": self.emoji,
            "review": review,
            "compliance_score": compliance.compliance_score,
            "timestamp": datetime.now().isoformat()
        }

    def __repr__(self):
        return f"{self.emoji} {self.nickname} ({self.role})"
