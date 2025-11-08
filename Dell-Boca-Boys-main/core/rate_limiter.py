"""
Production-grade rate limiting middleware for Dell Boca Boys V2.
Implements token bucket and sliding window algorithms with Redis backend.
"""
import asyncio
import time
import hashlib
from typing import Optional, Callable, Dict, Any
from dataclasses import dataclass
from functools import wraps
import logging

import redis.asyncio as aioredis

from core.exceptions import RateLimitExceededError

logger = logging.getLogger(__name__)


@dataclass
class RateLimitConfig:
    """Rate limit configuration."""
    requests: int  # Number of requests
    window: int    # Time window in seconds
    burst: Optional[int] = None  # Burst capacity (for token bucket)


class TokenBucketRateLimiter:
    """
    Token bucket rate limiter with Redis backend.

    Allows burst traffic while maintaining average rate limit.
    Each request consumes a token. Tokens are refilled at a constant rate.
    """

    def __init__(
        self,
        redis_client: aioredis.Redis,
        rate_config: RateLimitConfig,
        key_prefix: str = "rate_limit"
    ):
        """
        Initialize token bucket rate limiter.

        Args:
            redis_client: Async Redis client
            rate_config: Rate limit configuration
            key_prefix: Redis key prefix
        """
        self.redis = redis_client
        self.config = rate_config
        self.key_prefix = key_prefix

        # Calculate tokens per second
        self.refill_rate = rate_config.requests / rate_config.window

        # Burst capacity (defaults to rate if not specified)
        self.capacity = rate_config.burst or rate_config.requests

        logger.info(
            f"Token bucket rate limiter initialized: "
            f"{rate_config.requests} req/{rate_config.window}s, "
            f"burst={self.capacity}"
        )

    async def is_allowed(self, identifier: str, tokens: int = 1) -> tuple[bool, Dict[str, Any]]:
        """
        Check if request is allowed under rate limit.

        Args:
            identifier: Unique identifier (user_id, IP, etc.)
            tokens: Number of tokens to consume

        Returns:
            Tuple of (allowed, metadata)
            metadata contains: remaining, reset_time, retry_after
        """
        key = f"{self.key_prefix}:token_bucket:{identifier}"
        now = time.time()

        # Lua script for atomic token bucket operations
        lua_script = """
        local key = KEYS[1]
        local capacity = tonumber(ARGV[1])
        local refill_rate = tonumber(ARGV[2])
        local tokens_requested = tonumber(ARGV[3])
        local now = tonumber(ARGV[4])

        local bucket = redis.call('HMGET', key, 'tokens', 'last_refill')
        local tokens = tonumber(bucket[1]) or capacity
        local last_refill = tonumber(bucket[2]) or now

        -- Refill tokens based on elapsed time
        local elapsed = now - last_refill
        local tokens_to_add = elapsed * refill_rate
        tokens = math.min(capacity, tokens + tokens_to_add)

        -- Check if enough tokens available
        if tokens >= tokens_requested then
            tokens = tokens - tokens_requested
            redis.call('HMSET', key, 'tokens', tokens, 'last_refill', now)
            redis.call('EXPIRE', key, 3600)  -- 1 hour expiry
            return {1, tokens, now}  -- Allowed
        else
            redis.call('HMSET', key, 'tokens', tokens, 'last_refill', now)
            redis.call('EXPIRE', key, 3600)
            return {0, tokens, now}  -- Not allowed
        end
        """

        result = await self.redis.eval(
            lua_script,
            1,
            key,
            str(self.capacity),
            str(self.refill_rate),
            str(tokens),
            str(now)
        )

        allowed = bool(result[0])
        remaining_tokens = float(result[1])
        last_refill = float(result[2])

        # Calculate retry_after (seconds until enough tokens available)
        if not allowed:
            tokens_needed = tokens - remaining_tokens
            retry_after = int(tokens_needed / self.refill_rate) + 1
        else:
            retry_after = 0

        metadata = {
            "remaining": int(remaining_tokens),
            "limit": self.config.requests,
            "reset_time": int(last_refill + self.config.window),
            "retry_after": retry_after
        }

        return allowed, metadata


class SlidingWindowRateLimiter:
    """
    Sliding window rate limiter with Redis backend.

    Provides more accurate rate limiting than fixed windows by
    maintaining a sliding time window.
    """

    def __init__(
        self,
        redis_client: aioredis.Redis,
        rate_config: RateLimitConfig,
        key_prefix: str = "rate_limit"
    ):
        """
        Initialize sliding window rate limiter.

        Args:
            redis_client: Async Redis client
            rate_config: Rate limit configuration
            key_prefix: Redis key prefix
        """
        self.redis = redis_client
        self.config = rate_config
        self.key_prefix = key_prefix

        logger.info(
            f"Sliding window rate limiter initialized: "
            f"{rate_config.requests} req/{rate_config.window}s"
        )

    async def is_allowed(self, identifier: str) -> tuple[bool, Dict[str, Any]]:
        """
        Check if request is allowed under rate limit.

        Args:
            identifier: Unique identifier (user_id, IP, etc.)

        Returns:
            Tuple of (allowed, metadata)
        """
        key = f"{self.key_prefix}:sliding_window:{identifier}"
        now = time.time()
        window_start = now - self.config.window

        # Lua script for atomic sliding window operations
        lua_script = """
        local key = KEYS[1]
        local window_start = tonumber(ARGV[1])
        local now = tonumber(ARGV[2])
        local limit = tonumber(ARGV[3])
        local window = tonumber(ARGV[4])

        -- Remove old entries outside the window
        redis.call('ZREMRANGEBYSCORE', key, '-inf', window_start)

        -- Count requests in current window
        local count = redis.call('ZCARD', key)

        if count < limit then
            -- Add current request
            redis.call('ZADD', key, now, now)
            redis.call('EXPIRE', key, window * 2)
            return {1, count + 1}  -- Allowed
        else
            return {0, count}  -- Not allowed
        end
        """

        result = await self.redis.eval(
            lua_script,
            1,
            key,
            str(window_start),
            str(now),
            str(self.config.requests),
            str(self.config.window)
        )

        allowed = bool(result[0])
        current_count = int(result[1])

        # Calculate retry_after
        if not allowed:
            # Get oldest request timestamp
            oldest = await self.redis.zrange(key, 0, 0, withscores=True)
            if oldest:
                oldest_time = oldest[0][1]
                retry_after = int((oldest_time + self.config.window) - now) + 1
            else:
                retry_after = self.config.window
        else:
            retry_after = 0

        metadata = {
            "remaining": max(0, self.config.requests - current_count),
            "limit": self.config.requests,
            "reset_time": int(now + self.config.window),
            "retry_after": retry_after
        }

        return allowed, metadata


class RateLimiter:
    """
    Comprehensive rate limiter with multiple algorithms and tiers.

    Supports:
    - Per-user rate limiting
    - Per-IP rate limiting
    - Per-endpoint rate limiting
    - Global rate limiting
    - Tiered limits (e.g., free vs premium users)
    """

    def __init__(self, redis_url: str = "redis://localhost:6379/0"):
        """
        Initialize rate limiter.

        Args:
            redis_url: Redis connection URL
        """
        self.redis = aioredis.from_url(redis_url, decode_responses=False)
        self.limiters: Dict[str, Any] = {}
        self.logger = logging.getLogger(__name__)

    def create_limiter(
        self,
        name: str,
        rate_config: RateLimitConfig,
        algorithm: str = "token_bucket"
    ):
        """
        Create a rate limiter instance.

        Args:
            name: Limiter name/identifier
            rate_config: Rate limit configuration
            algorithm: "token_bucket" or "sliding_window"
        """
        if algorithm == "token_bucket":
            limiter = TokenBucketRateLimiter(self.redis, rate_config, key_prefix=f"rate_limit:{name}")
        elif algorithm == "sliding_window":
            limiter = SlidingWindowRateLimiter(self.redis, rate_config, key_prefix=f"rate_limit:{name}")
        else:
            raise ValueError(f"Unknown algorithm: {algorithm}")

        self.limiters[name] = limiter
        self.logger.info(f"Created {algorithm} rate limiter: {name}")
        return limiter

    async def check_limit(
        self,
        limiter_name: str,
        identifier: str,
        tokens: int = 1
    ) -> tuple[bool, Dict[str, Any]]:
        """
        Check rate limit for an identifier.

        Args:
            limiter_name: Name of the limiter to use
            identifier: Unique identifier
            tokens: Number of tokens to consume (for token bucket)

        Returns:
            Tuple of (allowed, metadata)

        Raises:
            ValueError: If limiter not found
        """
        if limiter_name not in self.limiters:
            raise ValueError(f"Rate limiter not found: {limiter_name}")

        limiter = self.limiters[limiter_name]

        if isinstance(limiter, TokenBucketRateLimiter):
            return await limiter.is_allowed(identifier, tokens)
        else:
            return await limiter.is_allowed(identifier)

    async def close(self):
        """Close Redis connection."""
        await self.redis.close()


# ============================================================================
# Rate Limiting Decorators
# ============================================================================

def rate_limit(
    limiter_name: str,
    get_identifier: Callable,
    limiter_instance: Optional[RateLimiter] = None
):
    """
    Decorator for rate limiting functions/endpoints.

    Args:
        limiter_name: Name of the rate limiter to use
        get_identifier: Function to extract identifier from args/kwargs
        limiter_instance: RateLimiter instance (optional, uses global if None)

    Example:
        @rate_limit(
            limiter_name="api_general",
            get_identifier=lambda *args, **kwargs: kwargs.get('user_id')
        )
        async def api_endpoint(user_id: str, data: dict):
            ...
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            identifier = get_identifier(*args, **kwargs)

            if limiter_instance:
                limiter = limiter_instance
            else:
                # Use global limiter
                limiter = get_global_rate_limiter()

            allowed, metadata = await limiter.check_limit(limiter_name, identifier)

            if not allowed:
                raise RateLimitExceededError(
                    endpoint=func.__name__,
                    limit=metadata['limit'],
                    window=metadata.get('reset_time', 0) - int(time.time()),
                    details=metadata
                )

            # Add rate limit info to response (if function returns dict)
            result = await func(*args, **kwargs)

            if isinstance(result, dict):
                result['_rate_limit'] = metadata

            return result

        return wrapper
    return decorator


# ============================================================================
# Global Rate Limiter Instance
# ============================================================================

_global_rate_limiter: Optional[RateLimiter] = None


def init_rate_limiter(redis_url: str = "redis://localhost:6379/0") -> RateLimiter:
    """Initialize global rate limiter."""
    global _global_rate_limiter
    _global_rate_limiter = RateLimiter(redis_url)
    return _global_rate_limiter


def get_global_rate_limiter() -> RateLimiter:
    """Get global rate limiter instance."""
    if _global_rate_limiter is None:
        raise RuntimeError("Rate limiter not initialized. Call init_rate_limiter() first.")
    return _global_rate_limiter


# ============================================================================
# Common Rate Limit Configurations
# ============================================================================

# API rate limits
API_RATE_LIMITS = {
    "strict": RateLimitConfig(requests=10, window=60, burst=15),      # 10 req/min
    "moderate": RateLimitConfig(requests=100, window=60, burst=150),  # 100 req/min
    "generous": RateLimitConfig(requests=1000, window=60, burst=1500), # 1000 req/min
}

# LLM rate limits (to protect expensive resources)
LLM_RATE_LIMITS = {
    "ollama_local": RateLimitConfig(requests=30, window=60, burst=40),   # 30 req/min
    "gemini_api": RateLimitConfig(requests=60, window=60, burst=80),     # 60 req/min
    "heavy_processing": RateLimitConfig(requests=5, window=60, burst=8), # 5 req/min
}

# User tier rate limits
USER_TIER_LIMITS = {
    "free": RateLimitConfig(requests=50, window=3600, burst=60),         # 50 req/hour
    "pro": RateLimitConfig(requests=500, window=3600, burst=600),        # 500 req/hour
    "enterprise": RateLimitConfig(requests=5000, window=3600, burst=6000), # 5000 req/hour
}
