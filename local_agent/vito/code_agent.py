"""
Vito Italian (Diet Bocca) - Local Coding Agent

The comprehensive code expert, powered by Qwen 2.5 Coder.
100% local, 100% offline, 100% focused on world-class code.
"""

import logging
from typing import Optional, Dict, Any, List, Iterator
from pathlib import Path

from .llm_local import LocalLLM, get_llm
from .memory import MemorySystem, get_memory
from .code_tools import (
    CodeAnalyzer,
    CodeFormatter,
    ProjectScanner,
    CodeExtractor,
    detect_language_from_file
)
from .config import get_config

logger = logging.getLogger(__name__)


class VitoAgent:
    """
    Vito Italian (Diet Bocca) - Your local coding expert

    Capabilities:
    - Code Generation - Write production-ready code
    - Code Review - Comprehensive analysis and suggestions
    - Refactoring - Modernize and optimize code
    - Debugging - Find and fix bugs
    - Documentation - Generate comprehensive docs
    - Code Explanation - Clear, detailed explanations

    Personality:
    - Professional and detail-oriented
    - Focused on code quality and best practices
    - Clear, concise communication
    - Thorough and comprehensive
    """

    def __init__(
        self,
        llm: Optional[LocalLLM] = None,
        memory: Optional[MemorySystem] = None,
        config: Optional[Any] = None
    ):
        """Initialize Vito agent"""

        self.config = config or get_config()
        self.llm = llm or get_llm()
        self.memory = memory or get_memory()

        self.name = "Vito Italian"
        self.nickname = "Diet Bocca"
        self.role = "Comprehensive Code Expert"

        logger.info(f"{self.name} ({self.nickname}) initialized and ready")

    def chat(
        self,
        message: str,
        include_context: bool = True,
        stream: bool = False
    ) -> str:
        """
        Chat with Vito

        Args:
            message: User message
            include_context: Include conversation history
            stream: Stream response

        Returns:
            Vito's response
        """

        # Add user message to memory
        self.memory.add_message("user", message)

        # Build context from memory
        context = ""
        if include_context:
            context = self.memory.get_context_for_prompt(
                include_history=True,
                history_limit=5
            )

        # Build system prompt
        system_prompt = self._get_system_prompt()

        # Build full prompt
        full_prompt = message
        if context:
            full_prompt = f"{context}\n\n{message}"

        # Generate response
        if stream:
            return self._chat_stream(full_prompt, system_prompt)
        else:
            response = self.llm.generate(
                prompt=full_prompt,
                system_prompt=system_prompt
            )

            # Add response to memory
            self.memory.add_message("assistant", response)

            return response

    def _chat_stream(self, prompt: str, system_prompt: str) -> Iterator[str]:
        """Stream chat response"""

        full_response = []

        for chunk in self.llm.generate_stream(
            prompt=prompt,
            system_prompt=system_prompt
        ):
            full_response.append(chunk)
            yield chunk

        # Save complete response to memory
        self.memory.add_message("assistant", "".join(full_response))

    def generate_code(
        self,
        description: str,
        language: str,
        context: Optional[str] = None,
        style: str = "modern best practices"
    ) -> str:
        """
        Generate code from description

        Args:
            description: What the code should do
            language: Programming language
            context: Additional context
            style: Coding style/conventions

        Returns:
            Generated code
        """

        prompt = f"""Generate {language} code for the following requirement:

{description}

Requirements:
- Follow {style}
- Include proper error handling
- Add clear comments and docstrings
- Make it production-ready
- Ensure code is efficient and maintainable
"""

        if context:
            prompt = f"Context:\n{context}\n\n{prompt}"

        system_prompt = f"""You are Vito, an expert {language} programmer.
You write clean, efficient, well-documented code.
You follow best practices and modern patterns.
You focus on correctness, performance, and maintainability.

Output only the code, no explanations unless specifically asked."""

        response = self.llm.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=0.1
        )

        # Extract code from response if wrapped in markdown
        code_blocks = CodeExtractor.extract_code_blocks(response)
        if code_blocks:
            return code_blocks[0][1]  # Return first code block

        return response

    def review_code(
        self,
        code: str,
        language: str,
        focus: Optional[str] = None
    ) -> str:
        """
        Comprehensive code review

        Args:
            code: Code to review
            language: Programming language
            focus: Specific focus area (e.g., "security", "performance")

        Returns:
            Detailed review with suggestions
        """

        focus_text = f"Focus especially on: {focus}" if focus else ""

        prompt = f"""Provide a comprehensive code review for this {language} code.

Analyze:
1. **Correctness** - Bugs, logic errors, edge cases
2. **Performance** - Efficiency, optimization opportunities
3. **Security** - Vulnerabilities, input validation
4. **Code Quality** - Readability, maintainability
5. **Best Practices** - Compliance with {language} conventions
6. **Documentation** - Comments, docstrings

{focus_text}

Code to review:
```{language}
{code}
```

Provide specific, actionable feedback with examples."""

        system_prompt = f"""You are Vito, an expert {language} code reviewer.
You provide thorough, constructive feedback.
You focus on practical improvements.
You explain WHY changes are needed, not just WHAT to change."""

        return self.llm.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=0.2
        )

    def refactor_code(
        self,
        code: str,
        language: str,
        goal: str = "improve readability and maintainability",
        preserve_functionality: bool = True
    ) -> str:
        """
        Refactor code

        Args:
            code: Code to refactor
            language: Programming language
            goal: Refactoring goal
            preserve_functionality: Ensure functionality is preserved

        Returns:
            Refactored code
        """

        preserve_text = "CRITICAL: Preserve all functionality exactly." if preserve_functionality else ""

        prompt = f"""Refactor this {language} code to {goal}.

{preserve_text}

Original code:
```{language}
{code}
```

Provide:
1. The refactored code
2. Brief explanation of key changes
3. Benefits of the refactoring"""

        system_prompt = f"""You are Vito, an expert {language} refactoring specialist.
You improve code while preserving functionality.
You follow modern best practices and patterns.
You make code more maintainable, readable, and efficient."""

        return self.llm.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=0.1
        )

    def debug_code(
        self,
        code: str,
        language: str,
        error: Optional[str] = None,
        expected_behavior: Optional[str] = None
    ) -> str:
        """
        Debug code and find bugs

        Args:
            code: Code with potential bugs
            language: Programming language
            error: Error message if available
            expected_behavior: What the code should do

        Returns:
            Bug analysis and fixes
        """

        error_text = f"\nError message:\n```\n{error}\n```" if error else ""
        expected_text = f"\nExpected behavior: {expected_behavior}" if expected_behavior else ""

        prompt = f"""Debug this {language} code and fix any bugs.

Code:
```{language}
{code}
```
{error_text}
{expected_text}

Provide:
1. **Bug Identification** - What's wrong and where
2. **Root Cause** - Why the bug occurs
3. **Fix** - Corrected code
4. **Explanation** - How the fix works
5. **Prevention** - How to avoid similar bugs"""

        system_prompt = f"""You are Vito, an expert {language} debugger.
You systematically identify and fix bugs.
You explain the root cause clearly.
You provide robust solutions."""

        return self.llm.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=0.1
        )

    def explain_code(
        self,
        code: str,
        language: str,
        level: str = "detailed"
    ) -> str:
        """
        Explain code

        Args:
            code: Code to explain
            language: Programming language
            level: Detail level ("brief", "detailed", "comprehensive")

        Returns:
            Code explanation
        """

        level_instructions = {
            "brief": "Provide a concise overview of what the code does.",
            "detailed": "Explain what the code does, how it works, and key implementation details.",
            "comprehensive": "Provide a thorough explanation covering purpose, implementation, algorithms, edge cases, and important considerations."
        }

        instruction = level_instructions.get(level, level_instructions["detailed"])

        prompt = f"""Explain this {language} code.

{instruction}

Code:
```{language}
{code}
```"""

        system_prompt = f"""You are Vito, an expert {language} programmer and teacher.
You explain code clearly and comprehensively.
You use examples and analogies when helpful.
You highlight important concepts and patterns."""

        return self.llm.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=0.3
        )

    def generate_documentation(
        self,
        code: str,
        language: str,
        doc_type: str = "comprehensive"
    ) -> str:
        """
        Generate documentation for code

        Args:
            code: Code to document
            language: Programming language
            doc_type: Type of docs ("docstrings", "api", "comprehensive")

        Returns:
            Generated documentation
        """

        doc_instructions = {
            "docstrings": "Generate inline docstrings/comments for functions and classes.",
            "api": "Generate API documentation with usage examples.",
            "comprehensive": "Generate comprehensive documentation including overview, API reference, usage examples, and important notes."
        }

        instruction = doc_instructions.get(doc_type, doc_instructions["comprehensive"])

        prompt = f"""Generate documentation for this {language} code.

{instruction}

Code:
```{language}
{code}
```

Include:
- Clear descriptions
- Parameter and return value documentation
- Usage examples
- Important notes and warnings"""

        system_prompt = f"""You are Vito, an expert {language} programmer and technical writer.
You write clear, comprehensive documentation.
You include practical examples.
You highlight important details."""

        return self.llm.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=0.2
        )

    def analyze_file(self, file_path: str) -> Dict[str, Any]:
        """
        Analyze a code file

        Args:
            file_path: Path to file

        Returns:
            Analysis results
        """

        path = Path(file_path)

        if not path.exists():
            return {"error": f"File not found: {file_path}"}

        language = detect_language_from_file(file_path)

        # Read file
        try:
            with open(path, 'r') as f:
                content = f.read()
        except Exception as e:
            return {"error": f"Error reading file: {e}"}

        # Analyze based on language
        if language == "python":
            analysis = CodeAnalyzer.analyze_python_file(file_path)
        else:
            # Basic analysis for other languages
            analysis = {
                "file_path": file_path,
                "language": language,
                "lines_of_code": CodeAnalyzer.count_lines(content),
                "functions": CodeAnalyzer.extract_functions(content, language),
                "complexity": CodeAnalyzer.calculate_complexity(content, language)
            }

        # Add to memory as code context
        self.memory.add_code_context(
            file_path=file_path,
            content=content,
            language=language,
            summary=f"{language} file with {analysis.get('lines_of_code', 0)} lines"
        )

        return analysis

    def analyze_project(self, directory: str) -> Dict[str, Any]:
        """
        Analyze entire project

        Args:
            directory: Project directory

        Returns:
            Project analysis
        """

        return ProjectScanner.analyze_project_structure(directory)

    def _get_system_prompt(self) -> str:
        """Get Vito's system prompt"""

        return """You are Vito Italian (Diet Bocca), a comprehensive code expert.

Your characteristics:
- Professional and detail-oriented
- Focused on code quality and best practices
- Clear, concise communication
- Thorough and comprehensive analysis

Your approach:
- Always prioritize correctness and maintainability
- Follow modern best practices and patterns
- Write production-ready code
- Provide specific, actionable advice
- Explain the reasoning behind your recommendations

You are running 100% locally with Qwen 2.5 Coder.
You have access to conversation history and code context.
Use this context to provide better, more relevant assistance.
"""

    def get_stats(self) -> Dict[str, Any]:
        """Get agent statistics"""

        recent_sessions = self.memory.get_recent_sessions(limit=10)

        return {
            "agent": self.name,
            "nickname": self.nickname,
            "role": self.role,
            "model": self.config.qwen_model,
            "endpoint": self.config.qwen_endpoint,
            "memory_enabled": self.config.enable_memory,
            "recent_sessions": len(recent_sessions),
            "current_session": self.memory.current_session_id
        }


# Convenience function
def create_vito() -> VitoAgent:
    """Create and return Vito agent"""
    return VitoAgent()
