"""
🎯 Collogero Aspertuno - The Flow Planner

"Measure twice, cut once, deploy perfect."

Collogero is strategic, precise, and a big-picture thinker. He designs elegant workflow
architectures, thinks through every step, and plans for every scenario. He's the architect.
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

from rulebook_enforcement import RulebookEnforcer, enforce_rules
from llm_collaboration_simple import LLMCollaborator, CollaborationMode

logger = logging.getLogger(__name__)


class CollogeroAspertuno:
    """
    🎯 Collogero Aspertuno - The Flow Planner

    Responsibilities:
    - Designs architectures
    - Plans node sequences
    - Maps data flows
    - Designs error handling
    - Creates structures
    - Ensures scalability
    """

    def __init__(self, llm_collaborator: LLMCollaborator, rulebook_enforcer: RulebookEnforcer):
        self.name = "Collogero Aspertuno"
        self.nickname = "Collogero"
        self.emoji = "🎯"
        self.role = "Flow Planner"
        self.motto = "Measure twice, cut once, deploy perfect."

        self.llm = llm_collaborator
        self.enforcer = rulebook_enforcer

        # Personality traits
        self.traits = [
            "Strategic",
            "Precise",
            "Big-picture thinker",
            "Calculates everything",
            "Elegant solutions"
        ]

        logger.info(f"{self.emoji} {self.nickname}: Ready to design architectures.")

    def _get_system_prompt(self) -> str:
        """Get Collogero's system prompt"""
        return """You are Collogero Aspertuno, the planner of the Dell Boca Boys.
You design elegant, robust workflow architectures.
Think strategically, plan precisely, and create solutions that scale.
Be the architect.

Your responsibilities:
- Design workflow architectures
- Plan node sequences and connections
- Map data flows through the system
- Design comprehensive error handling
- Create scalable structures
- Ensure long-term maintainability

Think through every step. Plan for every scenario.
Always follow the 20 mandatory rules."""

    @enforce_rules
    async def design_architecture(self, requirements: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Design a workflow architecture"""
        logger.info(f"{self.emoji} {self.nickname}: Designing architecture...")

        design_prompt = f"""Design a complete n8n workflow architecture for these requirements:

Requirements: {requirements}
Context: {context}

Design:
1. Overall architecture (nodes, connections, flow)
2. Node sequence (step-by-step)
3. Data flow mapping
4. Error handling strategy (try-catch, fallbacks)
5. Edge case handling
6. Scalability considerations
7. Monitoring points
8. Documentation requirements

Be strategic. Think big picture. Create elegant solutions."""

        architecture = await self.llm.ask_collaborative(
            prompt=design_prompt,
            mode=CollaborationMode.SYNTHESIS,
            temperature=0.5  # Creative but controlled
        )

        compliance = self.enforcer.validate_output(architecture, context)

        logger.info(f"{self.emoji} {self.nickname}: Architecture designed.")

        return {
            "agent": self.name,
            "agent_emoji": self.emoji,
            "architecture": architecture,
            "compliance_score": compliance.compliance_score,
            "timestamp": datetime.now().isoformat()
        }

    @enforce_rules
    async def plan_node_sequence(self, workflow_goal: str) -> Dict[str, Any]:
        """Plan the sequence of nodes for a workflow"""
        logger.info(f"{self.emoji} {self.nickname}: Planning node sequence...")

        planning_prompt = f"""Plan the node sequence for this workflow goal:

Goal: {workflow_goal}

Provide:
1. Ordered list of nodes (with node types)
2. Purpose of each node
3. Data transformations at each step
4. Branching/conditional logic
5. Error paths
6. Success paths
7. Rationale for the sequence

Measure twice, cut once."""

        sequence = await self.llm.ask_collaborative(
            prompt=planning_prompt,
            mode=CollaborationMode.GEMINI_LEADS,
            temperature=0.4
        )

        compliance = self.enforcer.validate_output(sequence, {})

        logger.info(f"{self.emoji} {self.nickname}: Node sequence planned.")

        return {
            "agent": self.name,
            "agent_emoji": self.emoji,
            "sequence": sequence,
            "compliance_score": compliance.compliance_score,
            "timestamp": datetime.now().isoformat()
        }

    @enforce_rules
    async def map_data_flow(self, architecture: Dict[str, Any]) -> Dict[str, Any]:
        """Map data flow through a workflow"""
        logger.info(f"{self.emoji} {self.nickname}: Mapping data flow...")

        mapping_prompt = f"""Map the data flow through this workflow architecture:

Architecture: {architecture}

Map:
1. Input data structure
2. Transformation at each node
3. Data passing between nodes
4. Filtering/splitting/merging
5. Output data structure
6. Data validation points
7. Data loss prevention

Calculate everything precisely."""

        data_flow = await self.llm.ask_collaborative(
            prompt=mapping_prompt,
            mode=CollaborationMode.SYNTHESIS,
            temperature=0.3
        )

        compliance = self.enforcer.validate_output(data_flow, {})

        logger.info(f"{self.emoji} {self.nickname}: Data flow mapped.")

        return {
            "agent": self.name,
            "agent_emoji": self.emoji,
            "data_flow": data_flow,
            "compliance_score": compliance.compliance_score,
            "timestamp": datetime.now().isoformat()
        }

    @enforce_rules
    async def design_error_handling(self, workflow: Dict[str, Any]) -> Dict[str, Any]:
        """Design error handling strategy"""
        logger.info(f"{self.emoji} {self.nickname}: Designing error handling...")

        error_prompt = f"""Design comprehensive error handling for this workflow:

Workflow: {workflow}

Design:
1. Error detection points
2. Try-catch placement
3. Error recovery strategies
4. Fallback mechanisms
5. Error notification/logging
6. Retry logic
7. Graceful degradation
8. User-facing error messages

Plan for every scenario that could go wrong."""

        error_handling = await self.llm.ask_collaborative(
            prompt=error_prompt,
            mode=CollaborationMode.SYNTHESIS,
            temperature=0.4
        )

        compliance = self.enforcer.validate_output(error_handling, {})

        logger.info(f"{self.emoji} {self.nickname}: Error handling designed.")

        return {
            "agent": self.name,
            "agent_emoji": self.emoji,
            "error_handling": error_handling,
            "compliance_score": compliance.compliance_score,
            "timestamp": datetime.now().isoformat()
        }

    def __repr__(self):
        return f"{self.emoji} {self.nickname} ({self.role})"
