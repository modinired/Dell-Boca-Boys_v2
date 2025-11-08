#!/usr/bin/env python3
"""
Advanced Redis Caching Layer for Dell-Boca-Boys
Provides intelligent caching for memory queries, workflows, and agent responses
"""
import redis
import json
import hashlib
import logging
from typing import Any, Optional, Callable, Dict
from functools import wraps
from datetime import timedelta
import pickle

logger = logging.getLogger(__name__)


class RedisCache:
    """
    Production-grade Redis caching with TTL, invalidation, and metrics.
    """

    def __init__(
        self,
        host: str = "localhost",
        port: int = 6379,
        db: int = 0,
        password: Optional[str] = None,
        default_ttl: int = 3600
    ):
        """
        Initialize Redis cache connection.

        Args:
            host: Redis server host
            port: Redis server port
            db: Redis database number
            password: Optional password for authentication
            default_ttl: Default time-to-live in seconds (1 hour)
        """
        self.client = redis.Redis(
            host=host,
            port=port,
            db=db,
            password=password,
            decode_responses=False,  # Handle binary data
            socket_keepalive=True,
            socket_connect_timeout=5,
            retry_on_timeout=True
        )
        self.default_ttl = default_ttl

        # Metrics
        self.hits = 0
        self.misses = 0

        # Test connection
        try:
            self.client.ping()
            logger.info(f"Connected to Redis at {host}:{port}")
        except redis.ConnectionError as e:
            logger.error(f"Failed to connect to Redis: {e}")
            raise

    def _generate_key(self, namespace: str, identifier: str) -> str:
        """Generate cache key with namespace prefix."""
        return f"dell_boca_boys:{namespace}:{identifier}"

    def _serialize(self, value: Any) -> bytes:
        """Serialize Python object for storage."""
        return pickle.dumps(value)

    def _deserialize(self, data: bytes) -> Any:
        """Deserialize stored data back to Python object."""
        return pickle.loads(data)

    def get(self, namespace: str, identifier: str) -> Optional[Any]:
        """
        Retrieve value from cache.

        Args:
            namespace: Cache namespace (e.g., "memory", "workflow", "agent")
            identifier: Unique identifier within namespace

        Returns:
            Cached value or None if not found/expired
        """
        key = self._generate_key(namespace, identifier)
        try:
            data = self.client.get(key)
            if data is not None:
                self.hits += 1
                logger.debug(f"Cache HIT: {key}")
                return self._deserialize(data)
            else:
                self.misses += 1
                logger.debug(f"Cache MISS: {key}")
                return None
        except Exception as e:
            logger.error(f"Cache get error for {key}: {e}")
            self.misses += 1
            return None

    def set(
        self,
        namespace: str,
        identifier: str,
        value: Any,
        ttl: Optional[int] = None
    ) -> bool:
        """
        Store value in cache with optional TTL.

        Args:
            namespace: Cache namespace
            identifier: Unique identifier
            value: Value to cache
            ttl: Time-to-live in seconds (uses default if None)

        Returns:
            True if successful, False otherwise
        """
        key = self._generate_key(namespace, identifier)
        ttl = ttl or self.default_ttl

        try:
            serialized = self._serialize(value)
            self.client.setex(key, ttl, serialized)
            logger.debug(f"Cache SET: {key} (TTL: {ttl}s)")
            return True
        except Exception as e:
            logger.error(f"Cache set error for {key}: {e}")
            return False

    def delete(self, namespace: str, identifier: str) -> bool:
        """Delete specific cache entry."""
        key = self._generate_key(namespace, identifier)
        try:
            result = self.client.delete(key)
            logger.debug(f"Cache DELETE: {key}")
            return result > 0
        except Exception as e:
            logger.error(f"Cache delete error for {key}: {e}")
            return False

    def invalidate_namespace(self, namespace: str) -> int:
        """
        Invalidate all keys in a namespace.

        Args:
            namespace: Namespace to clear

        Returns:
            Number of keys deleted
        """
        pattern = self._generate_key(namespace, "*")
        try:
            keys = self.client.keys(pattern)
            if keys:
                deleted = self.client.delete(*keys)
                logger.info(f"Invalidated {deleted} keys in namespace '{namespace}'")
                return deleted
            return 0
        except Exception as e:
            logger.error(f"Cache invalidation error for namespace {namespace}: {e}")
            return 0

    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        total_requests = self.hits + self.misses
        hit_rate = (self.hits / total_requests * 100) if total_requests > 0 else 0

        try:
            info = self.client.info("stats")
            memory_info = self.client.info("memory")

            return {
                "hits": self.hits,
                "misses": self.misses,
                "hit_rate": hit_rate,
                "total_requests": total_requests,
                "redis_keyspace_hits": info.get("keyspace_hits", 0),
                "redis_keyspace_misses": info.get("keyspace_misses", 0),
                "memory_used_bytes": memory_info.get("used_memory", 0),
                "memory_used_human": memory_info.get("used_memory_human", "0B"),
                "connected_clients": info.get("connected_clients", 0)
            }
        except Exception as e:
            logger.error(f"Error getting cache stats: {e}")
            return {
                "hits": self.hits,
                "misses": self.misses,
                "hit_rate": hit_rate,
                "total_requests": total_requests
            }

    def health_check(self) -> bool:
        """Check if Redis is responsive."""
        try:
            return self.client.ping()
        except Exception:
            return False


def cached(
    namespace: str,
    ttl: Optional[int] = None,
    key_builder: Optional[Callable] = None
):
    """
    Decorator for caching function results.

    Args:
        namespace: Cache namespace for this function
        ttl: Optional custom TTL
        key_builder: Optional function to build cache key from args/kwargs

    Example:
        @cached(namespace="memory_queries", ttl=600)
        def retrieve_memories(query: str, limit: int = 5):
            # Expensive operation
            return results
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Get or create cache instance (assumes global cache_client)
            from core.cache import cache_client

            # Build cache key
            if key_builder:
                cache_key = key_builder(*args, **kwargs)
            else:
                # Default: hash of function name + args + kwargs
                key_parts = [func.__name__, str(args), str(sorted(kwargs.items()))]
                cache_key = hashlib.sha256(
                    json.dumps(key_parts, sort_keys=True).encode()
                ).hexdigest()[:16]

            # Try to get from cache
            cached_result = cache_client.get(namespace, cache_key)
            if cached_result is not None:
                logger.debug(f"Using cached result for {func.__name__}")
                return cached_result

            # Execute function
            result = func(*args, **kwargs)

            # Store in cache
            cache_client.set(namespace, cache_key, result, ttl)

            return result

        return wrapper
    return decorator


# Global cache instance (initialized by application)
cache_client: Optional[RedisCache] = None


def init_cache(
    host: str = "localhost",
    port: int = 6379,
    db: int = 0,
    password: Optional[str] = None
) -> RedisCache:
    """Initialize global cache client."""
    global cache_client
    cache_client = RedisCache(host=host, port=port, db=db, password=password)
    return cache_client
