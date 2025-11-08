"""
Local LLM client for Qwen 2.5 Coder
100% offline, no cloud dependencies
"""

import logging
from typing import Optional, Iterator, Dict, Any, List
from openai import OpenAI
from datetime import datetime

from .config import get_config

logger = logging.getLogger(__name__)


class LocalLLM:
    """
    Local LLM client for Qwen 2.5 Coder

    Supports local Qwen deployment via:
    - vLLM (recommended)
    - Ollama
    - llama.cpp
    - LM Studio

    All use OpenAI-compatible API
    """

    def __init__(self, config: Optional[Any] = None):
        """Initialize local LLM client"""

        self.config = config or get_config()

        # Initialize OpenAI client pointing to local Qwen
        self.client = OpenAI(
            base_url=self.config.qwen_endpoint,
            api_key="not-needed-for-local",  # Local doesn't need API key
            timeout=self.config.timeout
        )

        self.model = self.config.qwen_model
        self.temperature = self.config.temperature
        self.max_tokens = self.config.max_tokens

        logger.info(f"Local LLM initialized: {self.config.qwen_endpoint}")

        # Test connection
        try:
            self._test_connection()
            logger.info("✓ Successfully connected to local Qwen")
        except Exception as e:
            logger.warning(f"Could not connect to Qwen at {self.config.qwen_endpoint}: {e}")
            logger.warning("Make sure Qwen is running locally!")

    def _test_connection(self):
        """Test connection to local Qwen"""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": "test"}],
                max_tokens=10,
                temperature=0.1
            )
            return response
        except Exception as e:
            raise ConnectionError(f"Cannot connect to Qwen: {e}")

    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        stop: Optional[List[str]] = None
    ) -> str:
        """
        Generate response from local Qwen

        Args:
            prompt: User prompt
            system_prompt: System prompt (optional)
            temperature: Temperature override
            max_tokens: Max tokens override
            stop: Stop sequences

        Returns:
            Generated text
        """

        messages = []

        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})

        messages.append({"role": "user", "content": prompt})

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature or self.temperature,
                max_tokens=max_tokens or self.max_tokens,
                stop=stop
            )

            return response.choices[0].message.content

        except Exception as e:
            logger.error(f"LLM generation error: {e}")
            raise

    def generate_stream(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> Iterator[str]:
        """
        Generate response with streaming

        Args:
            prompt: User prompt
            system_prompt: System prompt
            temperature: Temperature override
            max_tokens: Max tokens override

        Yields:
            Text chunks as they're generated
        """

        messages = []

        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})

        messages.append({"role": "user", "content": prompt})

        try:
            stream = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature or self.temperature,
                max_tokens=max_tokens or self.max_tokens,
                stream=True
            )

            for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content

        except Exception as e:
            logger.error(f"LLM streaming error: {e}")
            raise

    def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> str:
        """
        Multi-turn chat completion

        Args:
            messages: List of message dicts with 'role' and 'content'
            temperature: Temperature override
            max_tokens: Max tokens override

        Returns:
            Assistant's response
        """

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature or self.temperature,
                max_tokens=max_tokens or self.max_tokens
            )

            return response.choices[0].message.content

        except Exception as e:
            logger.error(f"Chat error: {e}")
            raise

    def code_completion(
        self,
        code: str,
        language: str,
        instruction: Optional[str] = None,
        max_tokens: Optional[int] = None
    ) -> str:
        """
        Code-specific completion optimized for Qwen Coder

        Args:
            code: Existing code
            language: Programming language
            instruction: What to do with the code
            max_tokens: Max tokens

        Returns:
            Completed/improved code
        """

        system_prompt = (
            f"You are an expert {language} programmer. "
            "You write clean, efficient, well-documented code. "
            "Follow best practices and modern patterns. "
            "Only output code, no explanations unless asked."
        )

        if instruction:
            prompt = f"{instruction}\n\n```{language}\n{code}\n```"
        else:
            prompt = f"Complete this {language} code:\n\n```{language}\n{code}\n```"

        return self.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=0.1,  # Low temperature for code
            max_tokens=max_tokens or self.max_tokens
        )

    def explain_code(self, code: str, language: str) -> str:
        """
        Explain what code does

        Args:
            code: Code to explain
            language: Programming language

        Returns:
            Detailed explanation
        """

        system_prompt = (
            f"You are an expert {language} programmer. "
            "Explain code clearly and comprehensively. "
            "Cover what it does, how it works, and any important details."
        )

        prompt = f"Explain this {language} code:\n\n```{language}\n{code}\n```"

        return self.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=0.3
        )

    def review_code(self, code: str, language: str) -> str:
        """
        Review code and suggest improvements

        Args:
            code: Code to review
            language: Programming language

        Returns:
            Code review with suggestions
        """

        system_prompt = (
            f"You are an expert {language} code reviewer. "
            "Analyze code for:\n"
            "1. Correctness and bugs\n"
            "2. Performance issues\n"
            "3. Security vulnerabilities\n"
            "4. Code quality and maintainability\n"
            "5. Best practices compliance\n"
            "Provide specific, actionable feedback."
        )

        prompt = f"Review this {language} code:\n\n```{language}\n{code}\n```"

        return self.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=0.2
        )

    def refactor_code(
        self,
        code: str,
        language: str,
        goal: str = "improve readability and maintainability"
    ) -> str:
        """
        Refactor code

        Args:
            code: Code to refactor
            language: Programming language
            goal: Refactoring goal

        Returns:
            Refactored code
        """

        system_prompt = (
            f"You are an expert {language} programmer specializing in refactoring. "
            "Improve code while preserving functionality. "
            "Follow modern best practices and patterns. "
            "Output only the refactored code."
        )

        prompt = (
            f"Refactor this {language} code to {goal}:\n\n"
            f"```{language}\n{code}\n```"
        )

        return self.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=0.1
        )

    def generate_docs(self, code: str, language: str) -> str:
        """
        Generate documentation for code

        Args:
            code: Code to document
            language: Programming language

        Returns:
            Documentation
        """

        system_prompt = (
            f"You are an expert {language} programmer and technical writer. "
            "Generate comprehensive documentation including:\n"
            "- Function/class descriptions\n"
            "- Parameter and return value docs\n"
            "- Usage examples\n"
            "- Important notes and warnings"
        )

        prompt = f"Generate documentation for this {language} code:\n\n```{language}\n{code}\n```"

        return self.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=0.2
        )

    def find_bugs(self, code: str, language: str, error: Optional[str] = None) -> str:
        """
        Find and fix bugs in code

        Args:
            code: Code with potential bugs
            language: Programming language
            error: Error message if available

        Returns:
            Bug analysis and fixes
        """

        system_prompt = (
            f"You are an expert {language} debugger. "
            "Analyze code for bugs and provide:\n"
            "1. What the bug is\n"
            "2. Why it occurs\n"
            "3. How to fix it\n"
            "4. Fixed code"
        )

        prompt = f"Find and fix bugs in this {language} code:\n\n```{language}\n{code}\n```"

        if error:
            prompt += f"\n\nError message:\n```\n{error}\n```"

        return self.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=0.1
        )


# Global instance
_llm: Optional[LocalLLM] = None


def get_llm() -> LocalLLM:
    """Get global LLM instance"""
    global _llm
    if _llm is None:
        _llm = LocalLLM()
    return _llm
