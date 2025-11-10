"""
Local Qwen LLM Client
Connects to local Qwen 2.5 Coder via OpenAI-compatible API (vLLM or Ollama)
"""

import logging
from typing import Dict, Optional, List, Any
from datetime import datetime
import asyncio
from dataclasses import dataclass, field

from openai import OpenAI, AsyncOpenAI
from openai import OpenAIError, APIError, APIConnectionError, RateLimitError

logger = logging.getLogger(__name__)


@dataclass
class GenerationMetrics:
    """Metrics for a generation request"""
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    latency_ms: float = 0.0
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    success: bool = True
    error: Optional[str] = None


@dataclass
class LocalModelConfig:
    """Configuration for local model"""
    endpoint: str
    model_name: str
    api_key: str = "not-needed"  # Most local endpoints don't need real API key
    max_tokens: int = 4096
    temperature: float = 0.1  # Low temperature for precise code generation
    top_p: float = 0.95
    timeout: int = 120  # 2 minutes default timeout
    max_retries: int = 3
    retry_delay: float = 1.0


class LocalQwenClient:
    """
    Client for local Qwen 2.5 Coder model via OpenAI-compatible API

    Supports both vLLM and Ollama endpoints
    Provides comprehensive error handling, retries, and metrics tracking
    """

    def __init__(self, config: LocalModelConfig):
        """
        Initialize local Qwen client

        Args:
            config: LocalModelConfig with endpoint and parameters
        """
        self.config = config

        # Initialize synchronous client
        self.client = OpenAI(
            base_url=config.endpoint,
            api_key=config.api_key,
            timeout=config.timeout
        )

        # Initialize async client
        self.async_client = AsyncOpenAI(
            base_url=config.endpoint,
            api_key=config.api_key,
            timeout=config.timeout
        )

        # Metrics tracking
        self.total_requests = 0
        self.successful_requests = 0
        self.failed_requests = 0
        self.total_tokens = 0
        self.total_latency_ms = 0.0

        logger.info(
            f"Initialized LocalQwenClient: endpoint={config.endpoint}, "
            f"model={config.model_name}, max_tokens={config.max_tokens}"
        )

    def generate(
        self,
        prompt: str,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> tuple[str, GenerationMetrics]:
        """
        Generate completion from local Qwen model (synchronous)

        Args:
            prompt: User prompt
            max_tokens: Override default max tokens
            temperature: Override default temperature
            system_prompt: Optional system prompt
            **kwargs: Additional parameters for chat completion

        Returns:
            Tuple of (generated_text, metrics)

        Raises:
            LocalModelError: If generation fails after retries
        """

        start_time = datetime.now()
        metrics = GenerationMetrics()

        # Build messages
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        # Parameters
        params = {
            "model": self.config.model_name,
            "messages": messages,
            "max_tokens": max_tokens or self.config.max_tokens,
            "temperature": temperature or self.config.temperature,
            "top_p": self.config.top_p,
            **kwargs
        }

        # Retry logic
        last_error = None
        for attempt in range(self.config.max_retries):
            try:
                logger.debug(f"Generating with local Qwen (attempt {attempt + 1}/{self.config.max_retries})")

                response = self.client.chat.completions.create(**params)

                # Extract response
                generated_text = response.choices[0].message.content

                # Extract metrics
                if hasattr(response, 'usage') and response.usage:
                    metrics.prompt_tokens = response.usage.prompt_tokens
                    metrics.completion_tokens = response.usage.completion_tokens
                    metrics.total_tokens = response.usage.total_tokens

                end_time = datetime.now()
                metrics.latency_ms = (end_time - start_time).total_seconds() * 1000
                metrics.success = True

                # Update global metrics
                self.total_requests += 1
                self.successful_requests += 1
                self.total_tokens += metrics.total_tokens
                self.total_latency_ms += metrics.latency_ms

                logger.info(
                    f"Local Qwen generation successful: {metrics.total_tokens} tokens in {metrics.latency_ms:.0f}ms"
                )

                return generated_text, metrics

            except APIConnectionError as e:
                last_error = e
                logger.warning(
                    f"Connection error to local Qwen (attempt {attempt + 1}/{self.config.max_retries}): {e}"
                )

                if attempt < self.config.max_retries - 1:
                    delay = self.config.retry_delay * (2 ** attempt)  # Exponential backoff
                    logger.info(f"Retrying in {delay:.1f}s...")
                    asyncio.sleep(delay)

            except RateLimitError as e:
                last_error = e
                logger.warning(f"Rate limit error from local Qwen: {e}")

                if attempt < self.config.max_retries - 1:
                    delay = self.config.retry_delay * 2
                    logger.info(f"Retrying in {delay:.1f}s...")
                    asyncio.sleep(delay)

            except APIError as e:
                last_error = e
                logger.error(f"API error from local Qwen: {e}")

                # Don't retry on 4xx errors (client errors)
                if hasattr(e, 'status_code') and 400 <= e.status_code < 500:
                    break

                if attempt < self.config.max_retries - 1:
                    delay = self.config.retry_delay
                    logger.info(f"Retrying in {delay:.1f}s...")
                    asyncio.sleep(delay)

            except Exception as e:
                last_error = e
                logger.error(f"Unexpected error in local Qwen generation: {e}", exc_info=True)
                break

        # All retries failed
        end_time = datetime.now()
        metrics.latency_ms = (end_time - start_time).total_seconds() * 1000
        metrics.success = False
        metrics.error = str(last_error)

        self.total_requests += 1
        self.failed_requests += 1

        error_msg = f"Local Qwen generation failed after {self.config.max_retries} attempts: {last_error}"
        logger.error(error_msg)

        raise LocalModelError(error_msg, original_error=last_error, metrics=metrics)

    async def generate_async(
        self,
        prompt: str,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> tuple[str, GenerationMetrics]:
        """
        Generate completion from local Qwen model (asynchronous)

        Args:
            prompt: User prompt
            max_tokens: Override default max tokens
            temperature: Override default temperature
            system_prompt: Optional system prompt
            **kwargs: Additional parameters for chat completion

        Returns:
            Tuple of (generated_text, metrics)

        Raises:
            LocalModelError: If generation fails after retries
        """

        start_time = datetime.now()
        metrics = GenerationMetrics()

        # Build messages
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        # Parameters
        params = {
            "model": self.config.model_name,
            "messages": messages,
            "max_tokens": max_tokens or self.config.max_tokens,
            "temperature": temperature or self.config.temperature,
            "top_p": self.config.top_p,
            **kwargs
        }

        # Retry logic
        last_error = None
        for attempt in range(self.config.max_retries):
            try:
                logger.debug(f"Generating with local Qwen async (attempt {attempt + 1}/{self.config.max_retries})")

                response = await self.async_client.chat.completions.create(**params)

                # Extract response
                generated_text = response.choices[0].message.content

                # Extract metrics
                if hasattr(response, 'usage') and response.usage:
                    metrics.prompt_tokens = response.usage.prompt_tokens
                    metrics.completion_tokens = response.usage.completion_tokens
                    metrics.total_tokens = response.usage.total_tokens

                end_time = datetime.now()
                metrics.latency_ms = (end_time - start_time).total_seconds() * 1000
                metrics.success = True

                # Update global metrics
                self.total_requests += 1
                self.successful_requests += 1
                self.total_tokens += metrics.total_tokens
                self.total_latency_ms += metrics.latency_ms

                logger.info(
                    f"Local Qwen async generation successful: {metrics.total_tokens} tokens in {metrics.latency_ms:.0f}ms"
                )

                return generated_text, metrics

            except APIConnectionError as e:
                last_error = e
                logger.warning(
                    f"Connection error to local Qwen (attempt {attempt + 1}/{self.config.max_retries}): {e}"
                )

                if attempt < self.config.max_retries - 1:
                    delay = self.config.retry_delay * (2 ** attempt)  # Exponential backoff
                    logger.info(f"Retrying in {delay:.1f}s...")
                    await asyncio.sleep(delay)

            except RateLimitError as e:
                last_error = e
                logger.warning(f"Rate limit error from local Qwen: {e}")

                if attempt < self.config.max_retries - 1:
                    delay = self.config.retry_delay * 2
                    logger.info(f"Retrying in {delay:.1f}s...")
                    await asyncio.sleep(delay)

            except APIError as e:
                last_error = e
                logger.error(f"API error from local Qwen: {e}")

                # Don't retry on 4xx errors (client errors)
                if hasattr(e, 'status_code') and 400 <= e.status_code < 500:
                    break

                if attempt < self.config.max_retries - 1:
                    delay = self.config.retry_delay
                    logger.info(f"Retrying in {delay:.1f}s...")
                    await asyncio.sleep(delay)

            except Exception as e:
                last_error = e
                logger.error(f"Unexpected error in local Qwen async generation: {e}", exc_info=True)
                break

        # All retries failed
        end_time = datetime.now()
        metrics.latency_ms = (end_time - start_time).total_seconds() * 1000
        metrics.success = False
        metrics.error = str(last_error)

        self.total_requests += 1
        self.failed_requests += 1

        error_msg = f"Local Qwen async generation failed after {self.config.max_retries} attempts: {last_error}"
        logger.error(error_msg)

        raise LocalModelError(error_msg, original_error=last_error, metrics=metrics)

    def health_check(self) -> Dict[str, Any]:
        """
        Check if local model is healthy and responsive

        Returns:
            Dictionary with health status
        """

        try:
            # Try a simple generation
            test_prompt = "Say 'OK' if you can read this."
            start_time = datetime.now()

            response = self.client.chat.completions.create(
                model=self.config.model_name,
                messages=[{"role": "user", "content": test_prompt}],
                max_tokens=10,
                temperature=0.0
            )

            end_time = datetime.now()
            latency_ms = (end_time - start_time).total_seconds() * 1000

            return {
                "status": "healthy",
                "endpoint": self.config.endpoint,
                "model": self.config.model_name,
                "latency_ms": latency_ms,
                "total_requests": self.total_requests,
                "successful_requests": self.successful_requests,
                "failed_requests": self.failed_requests,
                "success_rate": self.successful_requests / max(self.total_requests, 1),
                "avg_latency_ms": self.total_latency_ms / max(self.successful_requests, 1)
            }

        except Exception as e:
            logger.error(f"Health check failed: {e}")

            return {
                "status": "unhealthy",
                "endpoint": self.config.endpoint,
                "model": self.config.model_name,
                "error": str(e),
                "total_requests": self.total_requests,
                "successful_requests": self.successful_requests,
                "failed_requests": self.failed_requests
            }

    def get_metrics(self) -> Dict[str, Any]:
        """
        Get current usage metrics

        Returns:
            Dictionary with metrics
        """

        return {
            "total_requests": self.total_requests,
            "successful_requests": self.successful_requests,
            "failed_requests": self.failed_requests,
            "success_rate": self.successful_requests / max(self.total_requests, 1),
            "total_tokens": self.total_tokens,
            "avg_tokens_per_request": self.total_tokens / max(self.successful_requests, 1),
            "total_latency_ms": self.total_latency_ms,
            "avg_latency_ms": self.total_latency_ms / max(self.successful_requests, 1)
        }

    def reset_metrics(self):
        """Reset all metrics counters"""
        self.total_requests = 0
        self.successful_requests = 0
        self.failed_requests = 0
        self.total_tokens = 0
        self.total_latency_ms = 0.0
        logger.info("Metrics reset")


class LocalModelError(Exception):
    """Custom exception for local model errors"""

    def __init__(
        self,
        message: str,
        original_error: Optional[Exception] = None,
        metrics: Optional[GenerationMetrics] = None
    ):
        super().__init__(message)
        self.original_error = original_error
        self.metrics = metrics


# Factory function for easy initialization from config

def create_local_client_from_config(config_dict: Dict) -> LocalQwenClient:
    """
    Create LocalQwenClient from configuration dictionary

    Args:
        config_dict: Dictionary with configuration keys

    Returns:
        Initialized LocalQwenClient

    Example:
        config = {
            "endpoint": "http://localhost:11434/v1",
            "model_name": "qwen2.5-coder:32b",
            "max_tokens": 4096,
            "temperature": 0.1
        }
        client = create_local_client_from_config(config)
    """

    model_config = LocalModelConfig(
        endpoint=config_dict.get("endpoint", "http://localhost:11434/v1"),
        model_name=config_dict.get("model_name", "qwen2.5-coder:32b"),
        api_key=config_dict.get("api_key", "not-needed"),
        max_tokens=config_dict.get("max_tokens", 4096),
        temperature=config_dict.get("temperature", 0.1),
        top_p=config_dict.get("top_p", 0.95),
        timeout=config_dict.get("timeout", 120),
        max_retries=config_dict.get("max_retries", 3),
        retry_delay=config_dict.get("retry_delay", 1.0)
    )

    return LocalQwenClient(model_config)
