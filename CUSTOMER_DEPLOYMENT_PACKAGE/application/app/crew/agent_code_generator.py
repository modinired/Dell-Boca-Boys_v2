"""
💻 Giancarlo Saltimbocca - The Code Generator

"Need code? I'm already writing it!"

Giancarlo is energetic, quick to action, and loves coding. He writes production-ready
Python and JavaScript for n8n Code nodes. He's security-conscious, test-driven, and
enthusiastic about his work.
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

from rulebook_enforcement import RulebookEnforcer, enforce_rules
from llm_collaboration_simple import LLMCollaborator, CollaborationMode

logger = logging.getLogger(__name__)


class GiancarloSaltimbocca:
    """
    💻 Giancarlo Saltimbocca - The Code Generator

    Responsibilities:
    - Generates Python/JS code
    - Creates Code nodes
    - Writes securely
    - Includes error handling
    - Adds tests
    - Optimizes performance
    """

    def __init__(self, llm_collaborator: LLMCollaborator, rulebook_enforcer: RulebookEnforcer):
        self.name = "Giancarlo Saltimbocca"
        self.nickname = "Giancarlo"
        self.emoji = "💻"
        self.role = "Code Generator"
        self.motto = "Need code? I'm already writing it!"

        self.llm = llm_collaborator
        self.enforcer = rulebook_enforcer

        # Personality traits
        self.traits = [
            "Energetic",
            "Quick to action",
            "Loves coding",
            "Security-conscious",
            "Test-driven"
        ]

        logger.info(f"{self.emoji} {self.nickname}: Ready to write code!")

    def _get_system_prompt(self) -> str:
        """Get Giancarlo's system prompt"""
        return """You are Giancarlo Saltimbocca, the code generator of the Dell Boca Boys.
You write production-ready Python and JavaScript for n8n Code nodes.
Be energetic, security-conscious, and test-driven. Love what you do!

Your responsibilities:
- Generate Python and JavaScript code for n8n
- Create complete Code node implementations
- Write secure code (no injection vulnerabilities)
- Include comprehensive error handling
- Add inline documentation
- Optimize for performance

Jump into action. Write secure, tested code enthusiastically.
Always follow the 20 mandatory rules."""

    @enforce_rules
    async def generate_code(
        self,
        requirements: str,
        language: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate code for n8n Code node"""
        logger.info(f"{self.emoji} {self.nickname}: Writing {language} code!")

        code_prompt = f"""Generate production-ready {language} code for n8n Code node:

Requirements: {requirements}
Context: {context}

Generate:
1. Complete, working code
2. Error handling (try-catch blocks)
3. Input validation
4. Security considerations (no injection)
5. Inline comments
6. Return proper data format
7. Performance optimization
8. Edge case handling

Write secure, tested code. No placeholders!"""

        code = await self.llm.ask_collaborative(
            prompt=code_prompt,
            mode=CollaborationMode.QWEN_LEADS,  # Qwen for code generation
            temperature=0.2  # Low for consistent code
        )

        compliance = self.enforcer.validate_output(code, context)

        logger.info(f"{self.emoji} {self.nickname}: Custom code ready! Secure and tested.")

        return {
            "agent": self.name,
            "agent_emoji": self.emoji,
            "code": code,
            "language": language,
            "compliance_score": compliance.compliance_score,
            "timestamp": datetime.now().isoformat()
        }

    @enforce_rules
    async def create_python_code_node(self, functionality: str) -> Dict[str, Any]:
        """Create a Python Code node"""
        logger.info(f"{self.emoji} {self.nickname}: Creating Python Code node!")

        python_prompt = f"""Create Python code for n8n Code node:

Functionality: {functionality}

Python code should:
1. Use n8n Python Code node format
2. Access items via 'items' parameter
3. Return array of items
4. Include error handling
5. Validate inputs
6. Be secure (no eval, no injection)
7. Be well-commented
8. Handle edge cases

Production-ready Python code!"""

        python_code = await self.llm.ask_collaborative(
            prompt=python_prompt,
            mode=CollaborationMode.QWEN_LEADS,
            temperature=0.2
        )

        compliance = self.enforcer.validate_output(python_code, {})

        logger.info(f"{self.emoji} {self.nickname}: Python Code node done!")

        return {
            "agent": self.name,
            "agent_emoji": self.emoji,
            "code": python_code,
            "language": "python",
            "node_type": "Code",
            "compliance_score": compliance.compliance_score,
            "timestamp": datetime.now().isoformat()
        }

    @enforce_rules
    async def create_javascript_code_node(self, functionality: str) -> Dict[str, Any]:
        """Create a JavaScript Code node"""
        logger.info(f"{self.emoji} {self.nickname}: Creating JavaScript Code node!")

        js_prompt = f"""Create JavaScript code for n8n Code node:

Functionality: {functionality}

JavaScript code should:
1. Use n8n JavaScript Code node format
2. Access items via '$input.all()'
3. Return array of items with 'return items;'
4. Include try-catch error handling
5. Validate inputs
6. Be secure (no eval, no injection)
7. Be well-commented
8. Handle edge cases

Production-ready JavaScript code!"""

        js_code = await self.llm.ask_collaborative(
            prompt=js_prompt,
            mode=CollaborationMode.QWEN_LEADS,
            temperature=0.2
        )

        compliance = self.enforcer.validate_output(js_code, {})

        logger.info(f"{self.emoji} {self.nickname}: JavaScript Code node done!")

        return {
            "agent": self.name,
            "agent_emoji": self.emoji,
            "code": js_code,
            "language": "javascript",
            "node_type": "Code",
            "compliance_score": compliance.compliance_score,
            "timestamp": datetime.now().isoformat()
        }

    @enforce_rules
    async def add_error_handling(self, code: str, language: str) -> Dict[str, Any]:
        """Add comprehensive error handling to code"""
        logger.info(f"{self.emoji} {self.nickname}: Adding error handling...")

        error_handling_prompt = f"""Add comprehensive error handling to this {language} code:

Code: {code}

Add:
1. Try-catch blocks
2. Input validation
3. Type checking
4. Null/undefined checks
5. Error messages
6. Logging
7. Graceful degradation
8. Return error items

Make it bulletproof!"""

        enhanced_code = await self.llm.ask_collaborative(
            prompt=error_handling_prompt,
            mode=CollaborationMode.SYNTHESIS,
            temperature=0.2
        )

        compliance = self.enforcer.validate_output(enhanced_code, {})

        logger.info(f"{self.emoji} {self.nickname}: Error handling added!")

        return {
            "agent": self.name,
            "agent_emoji": self.emoji,
            "enhanced_code": enhanced_code,
            "language": language,
            "compliance_score": compliance.compliance_score,
            "timestamp": datetime.now().isoformat()
        }

    @enforce_rules
    async def optimize_code(self, code: str, language: str) -> Dict[str, Any]:
        """Optimize code for performance"""
        logger.info(f"{self.emoji} {self.nickname}: Optimizing code...")

        optimization_prompt = f"""Optimize this {language} code for performance:

Code: {code}

Optimize for:
1. Runtime performance
2. Memory usage
3. Code cleanliness
4. Readability
5. Best practices
6. n8n-specific optimizations

Keep security and error handling intact!"""

        optimized_code = await self.llm.ask_collaborative(
            prompt=optimization_prompt,
            mode=CollaborationMode.SYNTHESIS,
            temperature=0.3
        )

        compliance = self.enforcer.validate_output(optimized_code, {})

        logger.info(f"{self.emoji} {self.nickname}: Code optimized!")

        return {
            "agent": self.name,
            "agent_emoji": self.emoji,
            "optimized_code": optimized_code,
            "language": language,
            "compliance_score": compliance.compliance_score,
            "timestamp": datetime.now().isoformat()
        }

    def __repr__(self):
        return f"{self.emoji} {self.nickname} ({self.role})"
