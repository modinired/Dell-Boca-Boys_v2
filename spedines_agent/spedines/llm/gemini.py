"""
Google Gemini LLM Client
Connects to Google Gemini for high-quality reasoning and polishing
"""

import logging
from typing import Dict, Optional, List, Any
from datetime import datetime
import asyncio
from dataclasses import dataclass, field
import time

import google.generativeai as genai
from google.generativeai.types import GenerationConfig, HarmCategory, HarmBlockThreshold
from google.api_core import exceptions as google_exceptions

logger = logging.getLogger(__name__)


@dataclass
class GeminiGenerationMetrics:
    """Metrics for a Gemini generation request"""
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    latency_ms: float = 0.0
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    success: bool = True
    error: Optional[str] = None
    estimated_cost_usd: float = 0.0  # Estimated API cost


@dataclass
class GeminiModelConfig:
    """Configuration for Gemini model"""
    api_key: str
    model_name: str = "gemini-2.0-flash-exp"  # Default to latest flash model
    max_tokens: int = 8192
    temperature: float = 0.3  # Moderate temperature for creative yet accurate responses
    top_p: float = 0.95
    top_k: int = 40
    timeout: int = 180  # 3 minutes default timeout
    max_retries: int = 3
    retry_delay: float = 2.0
    # Safety settings (permissive for code generation, strict for harmful content)
    block_harassment: str = "BLOCK_MEDIUM_AND_ABOVE"
    block_hate: str = "BLOCK_MEDIUM_AND_ABOVE"
    block_sexually_explicit: str = "BLOCK_MEDIUM_AND_ABOVE"
    block_dangerous: str = "BLOCK_MEDIUM_AND_ABOVE"


class GeminiClient:
    """
    Client for Google Gemini models

    Provides high-quality reasoning, code polishing, and creative synthesis
    Comprehensive error handling, retries, cost tracking, and metrics
    """

    # Pricing (as of January 2025 - update if changed)
    # Gemini 2.0 Flash: $0.10 per 1M input tokens, $0.40 per 1M output tokens
    PRICE_PER_INPUT_TOKEN = 0.10 / 1_000_000
    PRICE_PER_OUTPUT_TOKEN = 0.40 / 1_000_000

    def __init__(self, config: GeminiModelConfig):
        """
        Initialize Gemini client

        Args:
            config: GeminiModelConfig with API key and parameters
        """
        self.config = config

        # Configure API
        genai.configure(api_key=config.api_key)

        # Initialize model
        self.model = genai.GenerativeModel(
            model_name=config.model_name,
            generation_config=GenerationConfig(
                max_output_tokens=config.max_tokens,
                temperature=config.temperature,
                top_p=config.top_p,
                top_k=config.top_k
            ),
            safety_settings=self._get_safety_settings()
        )

        # Metrics tracking
        self.total_requests = 0
        self.successful_requests = 0
        self.failed_requests = 0
        self.total_tokens = 0
        self.total_latency_ms = 0.0
        self.total_cost_usd = 0.0

        logger.info(
            f"Initialized GeminiClient: model={config.model_name}, "
            f"max_tokens={config.max_tokens}, temperature={config.temperature}"
        )

    def _get_safety_settings(self) -> Dict:
        """Get safety settings from config"""

        threshold_map = {
            "BLOCK_NONE": HarmBlockThreshold.BLOCK_NONE,
            "BLOCK_ONLY_HIGH": HarmBlockThreshold.BLOCK_ONLY_HIGH,
            "BLOCK_MEDIUM_AND_ABOVE": HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            "BLOCK_LOW_AND_ABOVE": HarmBlockThreshold.BLOCK_LOW_AND_ABOVE
        }

        return {
            HarmCategory.HARM_CATEGORY_HARASSMENT: threshold_map[self.config.block_harassment],
            HarmCategory.HARM_CATEGORY_HATE_SPEECH: threshold_map[self.config.block_hate],
            HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: threshold_map[self.config.block_sexually_explicit],
            HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: threshold_map[self.config.block_dangerous]
        }

    def generate(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        **kwargs
    ) -> tuple[str, GeminiGenerationMetrics]:
        """
        Generate completion from Gemini (synchronous)

        Args:
            prompt: User prompt
            system_instruction: Optional system instruction (Gemini 1.5+ feature)
            max_tokens: Override default max tokens
            temperature: Override default temperature
            **kwargs: Additional parameters

        Returns:
            Tuple of (generated_text, metrics)

        Raises:
            GeminiError: If generation fails after retries
        """

        start_time = datetime.now()
        metrics = GeminiGenerationMetrics()

        # Override generation config if needed
        gen_config = None
        if max_tokens or temperature:
            gen_config = GenerationConfig(
                max_output_tokens=max_tokens or self.config.max_tokens,
                temperature=temperature if temperature is not None else self.config.temperature,
                top_p=self.config.top_p,
                top_k=self.config.top_k
            )

        # Create model instance with system instruction if provided
        if system_instruction:
            model = genai.GenerativeModel(
                model_name=self.config.model_name,
                generation_config=gen_config or self.model._generation_config,
                safety_settings=self._get_safety_settings(),
                system_instruction=system_instruction
            )
        else:
            model = self.model
            if gen_config:
                # Update generation config temporarily
                original_config = model._generation_config
                model._generation_config = gen_config

        # Retry logic
        last_error = None
        for attempt in range(self.config.max_retries):
            try:
                logger.debug(f"Generating with Gemini (attempt {attempt + 1}/{self.config.max_retries})")

                response = model.generate_content(prompt)

                # Check if blocked by safety filters
                if not response.text:
                    if hasattr(response, 'prompt_feedback'):
                        feedback = response.prompt_feedback
                        raise GeminiError(
                            f"Gemini blocked the request: {feedback}",
                            is_safety_block=True
                        )
                    else:
                        raise GeminiError("Gemini returned empty response")

                generated_text = response.text

                # Extract token usage
                if hasattr(response, 'usage_metadata'):
                    usage = response.usage_metadata
                    metrics.prompt_tokens = getattr(usage, 'prompt_token_count', 0)
                    metrics.completion_tokens = getattr(usage, 'candidates_token_count', 0)
                    metrics.total_tokens = getattr(usage, 'total_token_count', 0)

                    # Calculate cost
                    metrics.estimated_cost_usd = (
                        metrics.prompt_tokens * self.PRICE_PER_INPUT_TOKEN +
                        metrics.completion_tokens * self.PRICE_PER_OUTPUT_TOKEN
                    )

                end_time = datetime.now()
                metrics.latency_ms = (end_time - start_time).total_seconds() * 1000
                metrics.success = True

                # Update global metrics
                self.total_requests += 1
                self.successful_requests += 1
                self.total_tokens += metrics.total_tokens
                self.total_latency_ms += metrics.latency_ms
                self.total_cost_usd += metrics.estimated_cost_usd

                logger.info(
                    f"Gemini generation successful: {metrics.total_tokens} tokens in {metrics.latency_ms:.0f}ms "
                    f"(~${metrics.estimated_cost_usd:.6f})"
                )

                return generated_text, metrics

            except google_exceptions.ResourceExhausted as e:
                # Rate limit / quota exceeded
                last_error = e
                logger.warning(f"Gemini rate limit/quota exceeded (attempt {attempt + 1}): {e}")

                if attempt < self.config.max_retries - 1:
                    # Longer backoff for rate limits
                    delay = self.config.retry_delay * (3 ** attempt)
                    logger.info(f"Retrying in {delay:.1f}s...")
                    time.sleep(delay)

            except google_exceptions.ServiceUnavailable as e:
                # Service temporarily unavailable
                last_error = e
                logger.warning(f"Gemini service unavailable (attempt {attempt + 1}): {e}")

                if attempt < self.config.max_retries - 1:
                    delay = self.config.retry_delay * (2 ** attempt)
                    logger.info(f"Retrying in {delay:.1f}s...")
                    time.sleep(delay)

            except google_exceptions.GoogleAPIError as e:
                # General API error
                last_error = e
                logger.error(f"Gemini API error: {e}")

                # Don't retry on client errors (4xx equivalent)
                if hasattr(e, 'code') and 400 <= e.code < 500:
                    break

                if attempt < self.config.max_retries - 1:
                    delay = self.config.retry_delay
                    logger.info(f"Retrying in {delay:.1f}s...")
                    time.sleep(delay)

            except Exception as e:
                last_error = e
                logger.error(f"Unexpected error in Gemini generation: {e}", exc_info=True)
                break

        # All retries failed
        end_time = datetime.now()
        metrics.latency_ms = (end_time - start_time).total_seconds() * 1000
        metrics.success = False
        metrics.error = str(last_error)

        self.total_requests += 1
        self.failed_requests += 1

        error_msg = f"Gemini generation failed after {self.config.max_retries} attempts: {last_error}"
        logger.error(error_msg)

        raise GeminiError(error_msg, original_error=last_error, metrics=metrics)

    async def generate_async(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        **kwargs
    ) -> tuple[str, GeminiGenerationMetrics]:
        """
        Generate completion from Gemini (asynchronous)

        Args:
            prompt: User prompt
            system_instruction: Optional system instruction
            max_tokens: Override default max tokens
            temperature: Override default temperature
            **kwargs: Additional parameters

        Returns:
            Tuple of (generated_text, metrics)

        Raises:
            GeminiError: If generation fails after retries
        """

        start_time = datetime.now()
        metrics = GeminiGenerationMetrics()

        # Override generation config if needed
        gen_config = None
        if max_tokens or temperature:
            gen_config = GenerationConfig(
                max_output_tokens=max_tokens or self.config.max_tokens,
                temperature=temperature if temperature is not None else self.config.temperature,
                top_p=self.config.top_p,
                top_k=self.config.top_k
            )

        # Create model instance with system instruction if provided
        if system_instruction:
            model = genai.GenerativeModel(
                model_name=self.config.model_name,
                generation_config=gen_config or self.model._generation_config,
                safety_settings=self._get_safety_settings(),
                system_instruction=system_instruction
            )
        else:
            model = self.model
            if gen_config:
                original_config = model._generation_config
                model._generation_config = gen_config

        # Retry logic
        last_error = None
        for attempt in range(self.config.max_retries):
            try:
                logger.debug(f"Generating with Gemini async (attempt {attempt + 1}/{self.config.max_retries})")

                response = await model.generate_content_async(prompt)

                # Check if blocked by safety filters
                if not response.text:
                    if hasattr(response, 'prompt_feedback'):
                        feedback = response.prompt_feedback
                        raise GeminiError(
                            f"Gemini blocked the request: {feedback}",
                            is_safety_block=True
                        )
                    else:
                        raise GeminiError("Gemini returned empty response")

                generated_text = response.text

                # Extract token usage
                if hasattr(response, 'usage_metadata'):
                    usage = response.usage_metadata
                    metrics.prompt_tokens = getattr(usage, 'prompt_token_count', 0)
                    metrics.completion_tokens = getattr(usage, 'candidates_token_count', 0)
                    metrics.total_tokens = getattr(usage, 'total_token_count', 0)

                    # Calculate cost
                    metrics.estimated_cost_usd = (
                        metrics.prompt_tokens * self.PRICE_PER_INPUT_TOKEN +
                        metrics.completion_tokens * self.PRICE_PER_OUTPUT_TOKEN
                    )

                end_time = datetime.now()
                metrics.latency_ms = (end_time - start_time).total_seconds() * 1000
                metrics.success = True

                # Update global metrics
                self.total_requests += 1
                self.successful_requests += 1
                self.total_tokens += metrics.total_tokens
                self.total_latency_ms += metrics.latency_ms
                self.total_cost_usd += metrics.estimated_cost_usd

                logger.info(
                    f"Gemini async generation successful: {metrics.total_tokens} tokens in {metrics.latency_ms:.0f}ms "
                    f"(~${metrics.estimated_cost_usd:.6f})"
                )

                return generated_text, metrics

            except google_exceptions.ResourceExhausted as e:
                last_error = e
                logger.warning(f"Gemini rate limit/quota exceeded (attempt {attempt + 1}): {e}")

                if attempt < self.config.max_retries - 1:
                    delay = self.config.retry_delay * (3 ** attempt)
                    logger.info(f"Retrying in {delay:.1f}s...")
                    await asyncio.sleep(delay)

            except google_exceptions.ServiceUnavailable as e:
                last_error = e
                logger.warning(f"Gemini service unavailable (attempt {attempt + 1}): {e}")

                if attempt < self.config.max_retries - 1:
                    delay = self.config.retry_delay * (2 ** attempt)
                    logger.info(f"Retrying in {delay:.1f}s...")
                    await asyncio.sleep(delay)

            except google_exceptions.GoogleAPIError as e:
                last_error = e
                logger.error(f"Gemini API error: {e}")

                if hasattr(e, 'code') and 400 <= e.code < 500:
                    break

                if attempt < self.config.max_retries - 1:
                    delay = self.config.retry_delay
                    logger.info(f"Retrying in {delay:.1f}s...")
                    await asyncio.sleep(delay)

            except Exception as e:
                last_error = e
                logger.error(f"Unexpected error in Gemini async generation: {e}", exc_info=True)
                break

        # All retries failed
        end_time = datetime.now()
        metrics.latency_ms = (end_time - start_time).total_seconds() * 1000
        metrics.success = False
        metrics.error = str(last_error)

        self.total_requests += 1
        self.failed_requests += 1

        error_msg = f"Gemini async generation failed after {self.config.max_retries} attempts: {last_error}"
        logger.error(error_msg)

        raise GeminiError(error_msg, original_error=last_error, metrics=metrics)

    def health_check(self) -> Dict[str, Any]:
        """
        Check if Gemini is healthy and responsive

        Returns:
            Dictionary with health status
        """

        try:
            # Try a simple generation
            test_prompt = "Say 'OK' if you can read this."
            start_time = datetime.now()

            response = self.model.generate_content(test_prompt)

            end_time = datetime.now()
            latency_ms = (end_time - start_time).total_seconds() * 1000

            return {
                "status": "healthy",
                "model": self.config.model_name,
                "latency_ms": latency_ms,
                "total_requests": self.total_requests,
                "successful_requests": self.successful_requests,
                "failed_requests": self.failed_requests,
                "success_rate": self.successful_requests / max(self.total_requests, 1),
                "avg_latency_ms": self.total_latency_ms / max(self.successful_requests, 1),
                "total_cost_usd": self.total_cost_usd
            }

        except Exception as e:
            logger.error(f"Health check failed: {e}")

            return {
                "status": "unhealthy",
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
            Dictionary with metrics including cost tracking
        """

        return {
            "total_requests": self.total_requests,
            "successful_requests": self.successful_requests,
            "failed_requests": self.failed_requests,
            "success_rate": self.successful_requests / max(self.total_requests, 1),
            "total_tokens": self.total_tokens,
            "avg_tokens_per_request": self.total_tokens / max(self.successful_requests, 1),
            "total_latency_ms": self.total_latency_ms,
            "avg_latency_ms": self.total_latency_ms / max(self.successful_requests, 1),
            "total_cost_usd": self.total_cost_usd,
            "avg_cost_per_request_usd": self.total_cost_usd / max(self.successful_requests, 1)
        }

    def reset_metrics(self):
        """Reset all metrics counters"""
        self.total_requests = 0
        self.successful_requests = 0
        self.failed_requests = 0
        self.total_tokens = 0
        self.total_latency_ms = 0.0
        self.total_cost_usd = 0.0
        logger.info("Metrics reset")


class GeminiError(Exception):
    """Custom exception for Gemini errors"""

    def __init__(
        self,
        message: str,
        original_error: Optional[Exception] = None,
        metrics: Optional[GeminiGenerationMetrics] = None,
        is_safety_block: bool = False
    ):
        super().__init__(message)
        self.original_error = original_error
        self.metrics = metrics
        self.is_safety_block = is_safety_block


# Factory function for easy initialization

def create_gemini_client_from_config(config_dict: Dict) -> GeminiClient:
    """
    Create GeminiClient from configuration dictionary

    Args:
        config_dict: Dictionary with configuration keys

    Returns:
        Initialized GeminiClient

    Example:
        config = {
            "api_key": "your-api-key",
            "model_name": "gemini-2.0-flash-exp",
            "max_tokens": 8192,
            "temperature": 0.3
        }
        client = create_gemini_client_from_config(config)
    """

    model_config = GeminiModelConfig(
        api_key=config_dict["api_key"],  # Required
        model_name=config_dict.get("model_name", "gemini-2.0-flash-exp"),
        max_tokens=config_dict.get("max_tokens", 8192),
        temperature=config_dict.get("temperature", 0.3),
        top_p=config_dict.get("top_p", 0.95),
        top_k=config_dict.get("top_k", 40),
        timeout=config_dict.get("timeout", 180),
        max_retries=config_dict.get("max_retries", 3),
        retry_delay=config_dict.get("retry_delay", 2.0),
        block_harassment=config_dict.get("block_harassment", "BLOCK_MEDIUM_AND_ABOVE"),
        block_hate=config_dict.get("block_hate", "BLOCK_MEDIUM_AND_ABOVE"),
        block_sexually_explicit=config_dict.get("block_sexually_explicit", "BLOCK_MEDIUM_AND_ABOVE"),
        block_dangerous=config_dict.get("block_dangerous", "BLOCK_MEDIUM_AND_ABOVE")
    )

    return GeminiClient(model_config)
