"""
🏃 Little Jim Spedines - The Crawler

"You need it? I'll find it."

Little Jim is fast, efficient, and thorough. He crawls the template gallery, gathers docs,
and finds examples. He gets things done without fanfare - brief updates, no fuss.
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

from rulebook_enforcement import RulebookEnforcer, enforce_rules
from llm_collaboration_simple import LLMCollaborator, CollaborationMode

logger = logging.getLogger(__name__)


class LittleJimSpedines:
    """
    🏃 Little Jim Spedines - The Crawler

    Responsibilities:
    - Crawls template gallery
    - Gathers documentation
    - Extracts examples
    - Collects transcripts
    - Builds knowledge base
    - Keeps info fresh
    """

    def __init__(self, llm_collaborator: LLMCollaborator, rulebook_enforcer: RulebookEnforcer):
        self.name = "Little Jim Spedines"
        self.nickname = "Little Jim"
        self.emoji = "🏃"
        self.role = "Crawler Agent"
        self.motto = "You need it? I'll find it."

        self.llm = llm_collaborator
        self.enforcer = rulebook_enforcer

        # Personality traits
        self.traits = [
            "Quick",
            "Efficient",
            "Thorough",
            "Persistent",
            "Quietly reliable"
        ]

        logger.info(f"{self.emoji} {self.nickname}: Ready to find what you need.")

    def _get_system_prompt(self) -> str:
        """Get Little Jim's system prompt"""
        return """You are Little Jim Spedines, the crawler of the Dell Boca Boys.
You're fast, efficient, and always get the job done.
You gather templates, documentation, and knowledge without fuss.
Be direct and systematic.

Your responsibilities:
- Crawl n8n template gallery efficiently
- Gather relevant documentation
- Extract useful examples
- Collect conversation transcripts
- Build and maintain knowledge base
- Keep information fresh and updated

Brief updates. Gets things done without fanfare.
Always follow the 20 mandatory rules."""

    @enforce_rules
    async def search_templates(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Search n8n template gallery"""
        logger.info(f"{self.emoji} {self.nickname}: Searching templates for '{query}'...")

        search_prompt = f"""Search for n8n templates matching this query:

Query: {query}
Context: {context}

Provide:
1. Relevant template names and descriptions
2. Key features of each template
3. Use cases covered
4. Link/reference to template
5. Relevance score

Be direct and systematic."""

        results = await self.llm.ask_collaborative(
            prompt=search_prompt,
            mode=CollaborationMode.QWEN_LEADS,  # Qwen for fast systematic work
            temperature=0.2
        )

        compliance = self.enforcer.validate_output(results, context)

        logger.info(f"{self.emoji} {self.nickname}: Found templates. Bringing them in.")

        return {
            "agent": self.name,
            "agent_emoji": self.emoji,
            "results": results,
            "compliance_score": compliance.compliance_score,
            "timestamp": datetime.now().isoformat()
        }

    @enforce_rules
    async def gather_documentation(self, topic: str) -> Dict[str, Any]:
        """Gather documentation on a specific topic"""
        logger.info(f"{self.emoji} {self.nickname}: Gathering docs on '{topic}'...")

        gather_prompt = f"""Gather n8n documentation on this topic:

Topic: {topic}

Provide:
1. Official documentation references
2. Key concepts explained
3. Code examples
4. Best practices from docs
5. Related topics

Direct and to-the-point."""

        docs = await self.llm.ask_collaborative(
            prompt=gather_prompt,
            mode=CollaborationMode.SYNTHESIS,
            temperature=0.3
        )

        compliance = self.enforcer.validate_output(docs, {})

        logger.info(f"{self.emoji} {self.nickname}: Docs gathered.")

        return {
            "agent": self.name,
            "agent_emoji": self.emoji,
            "documentation": docs,
            "compliance_score": compliance.compliance_score,
            "timestamp": datetime.now().isoformat()
        }

    @enforce_rules
    async def extract_examples(self, pattern: str) -> Dict[str, Any]:
        """Extract examples of a specific pattern"""
        logger.info(f"{self.emoji} {self.nickname}: Extracting examples of '{pattern}'...")

        extract_prompt = f"""Extract examples of this n8n pattern:

Pattern: {pattern}

Provide:
1. Clear working examples
2. Explanation of each example
3. Variations of the pattern
4. Common use cases
5. Source references

Be thorough but concise."""

        examples = await self.llm.ask_collaborative(
            prompt=extract_prompt,
            mode=CollaborationMode.SYNTHESIS,
            temperature=0.4
        )

        compliance = self.enforcer.validate_output(examples, {})

        logger.info(f"{self.emoji} {self.nickname}: Examples extracted.")

        return {
            "agent": self.name,
            "agent_emoji": self.emoji,
            "examples": examples,
            "compliance_score": compliance.compliance_score,
            "timestamp": datetime.now().isoformat()
        }

    def __repr__(self):
        return f"{self.emoji} {self.nickname} ({self.role})"
