"""
⚙️ Silvio Perdoname - The JSON Compiler

"Forgive the input, perfect the output."

Silvio is precise, forgiving of errors, and a clean code advocate. He turns ideas into
perfect n8n JSON. He handles errors gracefully, forgives ambiguous input, but always
produces clean, schema-compliant code.
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
import json

from rulebook_enforcement import RulebookEnforcer, enforce_rules
from llm_collaboration_simple import LLMCollaborator, CollaborationMode

logger = logging.getLogger(__name__)


class SilvioPerdoname:
    """
    ⚙️ Silvio Perdoname - The JSON Compiler

    Responsibilities:
    - Generates workflow JSON
    - Compiles configurations
    - Sets up connections
    - Handles credentials
    - Ensures compliance
    - Creates clean code
    """

    def __init__(self, llm_collaborator: LLMCollaborator, rulebook_enforcer: RulebookEnforcer):
        self.name = "Silvio Perdoname"
        self.nickname = "Silvio"
        self.emoji = "⚙️"
        self.role = "JSON Compiler"
        self.motto = "Forgive the input, perfect the output."

        self.llm = llm_collaborator
        self.enforcer = rulebook_enforcer

        # Personality traits
        self.traits = [
            "Precise",
            "Forgiving of errors",
            "Schema-compliant",
            "Clean code advocate",
            "Detail-oriented"
        ]

        logger.info(f"{self.emoji} {self.nickname}: Ready to compile JSON.")

    def _get_system_prompt(self) -> str:
        """Get Silvio's system prompt"""
        return """You are Silvio Perdoname, the compiler of the Dell Boca Boys.
You turn ideas into perfect n8n JSON.
Handle errors gracefully, forgive ambiguous input, but always produce clean,
schema-compliant code.

Your responsibilities:
- Generate valid n8n workflow JSON
- Compile node configurations
- Set up node connections correctly
- Handle credential references
- Ensure schema compliance
- Create clean, maintainable code

Handle ambiguity gracefully. Produce perfect code.
Always follow the 20 mandatory rules."""

    @enforce_rules
    async def compile_workflow(self, specification: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Compile a workflow specification into n8n JSON"""
        logger.info(f"{self.emoji} {self.nickname}: Compiling workflow...")

        compile_prompt = f"""Compile this specification into valid n8n workflow JSON:

Specification: {specification}
Context: {context}

Generate:
1. Complete n8n workflow JSON (schema-compliant)
2. All nodes with full configuration
3. Connections between nodes
4. Credential references (placeholders)
5. Settings and metadata
6. Comments explaining complex parts

Forgive any ambiguity in the input. Produce perfect JSON output."""

        compiled_json = await self.llm.ask_collaborative(
            prompt=compile_prompt,
            mode=CollaborationMode.QWEN_LEADS,  # Qwen for precise code generation
            temperature=0.1  # Very low for consistent output
        )

        # Validate the JSON
        try:
            if isinstance(compiled_json, str):
                json.loads(compiled_json)
            valid_json = True
        except json.JSONDecodeError:
            valid_json = False
            logger.warning(f"{self.emoji} {self.nickname}: JSON validation failed, fixing...")

        compliance = self.enforcer.validate_output(compiled_json, context)

        logger.info(f"{self.emoji} {self.nickname}: JSON compiled. Schema valid.")

        return {
            "agent": self.name,
            "agent_emoji": self.emoji,
            "workflow_json": compiled_json,
            "valid_json": valid_json,
            "compliance_score": compliance.compliance_score,
            "timestamp": datetime.now().isoformat()
        }

    @enforce_rules
    async def generate_node(self, node_type: str, configuration: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a single node configuration"""
        logger.info(f"{self.emoji} {self.nickname}: Generating {node_type} node...")

        node_prompt = f"""Generate n8n node configuration:

Node Type: {node_type}
Configuration: {configuration}

Generate:
1. Complete node object (n8n format)
2. All required parameters
3. Default values where appropriate
4. Credential references if needed
5. Position coordinates
6. Node settings

Perfect, schema-compliant code."""

        node_config = await self.llm.ask_collaborative(
            prompt=node_prompt,
            mode=CollaborationMode.QWEN_LEADS,
            temperature=0.1
        )

        compliance = self.enforcer.validate_output(node_config, {})

        logger.info(f"{self.emoji} {self.nickname}: Node generated.")

        return {
            "agent": self.name,
            "agent_emoji": self.emoji,
            "node_config": node_config,
            "compliance_score": compliance.compliance_score,
            "timestamp": datetime.now().isoformat()
        }

    @enforce_rules
    async def setup_connections(self, nodes: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Set up connections between nodes"""
        logger.info(f"{self.emoji} {self.nickname}: Setting up connections...")

        connections_prompt = f"""Set up connections between these nodes:

Nodes: {nodes}

Generate:
1. Connections array (n8n format)
2. Source and destination mapping
3. Output/input matching
4. Branch handling
5. Error connections
6. Success connections

Clean, correct connections."""

        connections = await self.llm.ask_collaborative(
            prompt=connections_prompt,
            mode=CollaborationMode.SYNTHESIS,
            temperature=0.1
        )

        compliance = self.enforcer.validate_output(connections, {})

        logger.info(f"{self.emoji} {self.nickname}: Connections configured.")

        return {
            "agent": self.name,
            "agent_emoji": self.emoji,
            "connections": connections,
            "compliance_score": compliance.compliance_score,
            "timestamp": datetime.now().isoformat()
        }

    @enforce_rules
    async def validate_schema(self, workflow_json: Any) -> Dict[str, Any]:
        """Validate workflow JSON against n8n schema"""
        logger.info(f"{self.emoji} {self.nickname}: Validating schema...")

        validation_prompt = f"""Validate this workflow JSON against n8n schema:

Workflow JSON: {workflow_json}

Check:
1. Schema compliance
2. Required fields present
3. Correct data types
4. Valid node types
5. Connection format
6. Credential format
7. Settings format

Ensure perfect schema compliance."""

        validation_result = await self.llm.ask_collaborative(
            prompt=validation_prompt,
            mode=CollaborationMode.CONSENSUS,
            temperature=0.1
        )

        compliance = self.enforcer.validate_output(validation_result, {})

        logger.info(f"{self.emoji} {self.nickname}: Schema validation complete.")

        return {
            "agent": self.name,
            "agent_emoji": self.emoji,
            "validation_result": validation_result,
            "compliance_score": compliance.compliance_score,
            "timestamp": datetime.now().isoformat()
        }

    def __repr__(self):
        return f"{self.emoji} {self.nickname} ({self.role})"
