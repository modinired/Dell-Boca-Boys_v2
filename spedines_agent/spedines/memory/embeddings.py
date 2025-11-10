"""
Embedding Generation for Memory System
Uses sentence-transformers for local, high-quality embeddings
"""

import logging
from typing import List, Optional, Union
import time
from dataclasses import dataclass

import numpy as np
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)


@dataclass
class EmbeddingConfig:
    """Configuration for embedding generation"""
    model_name: str = "all-MiniLM-L6-v2"  # Fast, lightweight model (384 dimensions)
    # Alternatives:
    # - "all-mpnet-base-v2" - Higher quality (768 dims), slower
    # - "paraphrase-multilingual-MiniLM-L12-v2" - Multilingual support
    device: str = "cpu"  # or "cuda" if GPU available
    batch_size: int = 32
    normalize_embeddings: bool = True  # Normalize for cosine similarity
    show_progress_bar: bool = False


class EmbeddingGenerator:
    """
    Generate embeddings for text using sentence-transformers

    Provides fast, high-quality embeddings for semantic search
    Runs entirely locally - no API calls required
    """

    def __init__(self, config: EmbeddingConfig):
        """
        Initialize embedding generator

        Args:
            config: EmbeddingConfig with model and parameters
        """
        self.config = config

        logger.info(f"Loading embedding model: {config.model_name}")
        start_time = time.time()

        try:
            self.model = SentenceTransformer(
                config.model_name,
                device=config.device
            )

            load_time = time.time() - start_time
            logger.info(
                f"Embedding model loaded in {load_time:.2f}s "
                f"(dimensions: {self.model.get_sentence_embedding_dimension()})"
            )

        except Exception as e:
            logger.error(f"Failed to load embedding model: {e}")
            raise

        # Metrics
        self.total_embeddings = 0
        self.total_time = 0.0

    def embed(
        self,
        texts: Union[str, List[str]],
        batch_size: Optional[int] = None,
        show_progress: Optional[bool] = None
    ) -> np.ndarray:
        """
        Generate embeddings for text(s)

        Args:
            texts: Single text or list of texts
            batch_size: Override default batch size
            show_progress: Override default progress bar setting

        Returns:
            Numpy array of embeddings
            - Single text: shape (embedding_dim,)
            - Multiple texts: shape (num_texts, embedding_dim)
        """

        # Handle single text
        single_input = isinstance(texts, str)
        if single_input:
            texts = [texts]

        start_time = time.time()

        try:
            embeddings = self.model.encode(
                texts,
                batch_size=batch_size or self.config.batch_size,
                normalize_embeddings=self.config.normalize_embeddings,
                show_progress_bar=show_progress if show_progress is not None else self.config.show_progress_bar
            )

            # Convert to numpy array if not already
            if not isinstance(embeddings, np.ndarray):
                embeddings = np.array(embeddings)

            # Update metrics
            elapsed = time.time() - start_time
            self.total_embeddings += len(texts)
            self.total_time += elapsed

            logger.debug(
                f"Generated {len(texts)} embeddings in {elapsed:.3f}s "
                f"({len(texts)/elapsed:.1f} embeddings/sec)"
            )

            # Return single embedding as 1D array
            if single_input:
                return embeddings[0]

            return embeddings

        except Exception as e:
            logger.error(f"Embedding generation failed: {e}")
            raise EmbeddingError(f"Failed to generate embeddings: {e}")

    async def embed_async(
        self,
        texts: Union[str, List[str]],
        batch_size: Optional[int] = None,
        show_progress: Optional[bool] = None
    ) -> np.ndarray:
        """
        Generate embeddings asynchronously

        Note: sentence-transformers is CPU-bound, so this uses the sync method
        wrapped in an executor to avoid blocking the event loop

        Args:
            texts: Single text or list of texts
            batch_size: Override default batch size
            show_progress: Override default progress bar setting

        Returns:
            Numpy array of embeddings
        """

        import asyncio

        # Run in thread pool executor to avoid blocking
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            self.embed,
            texts,
            batch_size,
            show_progress
        )

    def embed_batch(
        self,
        texts: List[str],
        batch_size: Optional[int] = None,
        show_progress: bool = True
    ) -> np.ndarray:
        """
        Generate embeddings for large batch of texts

        More efficient than calling embed() multiple times

        Args:
            texts: List of texts
            batch_size: Batch size for processing
            show_progress: Show progress bar

        Returns:
            Numpy array of shape (len(texts), embedding_dim)
        """

        if not texts:
            raise ValueError("Cannot embed empty list")

        logger.info(f"Generating embeddings for {len(texts)} texts")

        return self.embed(
            texts,
            batch_size=batch_size,
            show_progress=show_progress
        )

    def cosine_similarity(
        self,
        embedding1: np.ndarray,
        embedding2: np.ndarray
    ) -> float:
        """
        Calculate cosine similarity between two embeddings

        Args:
            embedding1: First embedding vector
            embedding2: Second embedding vector

        Returns:
            Similarity score from -1 (opposite) to 1 (identical)
            Typically in range [0, 1] for normalized embeddings
        """

        # Handle both 1D and 2D arrays
        if embedding1.ndim > 1:
            embedding1 = embedding1.flatten()
        if embedding2.ndim > 1:
            embedding2 = embedding2.flatten()

        # If embeddings are normalized, dot product equals cosine similarity
        if self.config.normalize_embeddings:
            return float(np.dot(embedding1, embedding2))

        # Otherwise calculate manually
        norm1 = np.linalg.norm(embedding1)
        norm2 = np.linalg.norm(embedding2)

        if norm1 == 0 or norm2 == 0:
            return 0.0

        return float(np.dot(embedding1, embedding2) / (norm1 * norm2))

    def find_most_similar(
        self,
        query_embedding: np.ndarray,
        candidate_embeddings: np.ndarray,
        top_k: int = 5
    ) -> List[tuple[int, float]]:
        """
        Find most similar embeddings to query

        Args:
            query_embedding: Query embedding (1D array)
            candidate_embeddings: Candidate embeddings (2D array)
            top_k: Number of top results to return

        Returns:
            List of (index, similarity) tuples, sorted by similarity (descending)
        """

        # Ensure correct shapes
        if query_embedding.ndim > 1:
            query_embedding = query_embedding.flatten()

        if candidate_embeddings.ndim == 1:
            candidate_embeddings = candidate_embeddings.reshape(1, -1)

        # Calculate all similarities
        if self.config.normalize_embeddings:
            # Dot product for normalized embeddings
            similarities = np.dot(candidate_embeddings, query_embedding)
        else:
            # Cosine similarity
            norms = np.linalg.norm(candidate_embeddings, axis=1)
            query_norm = np.linalg.norm(query_embedding)

            if query_norm == 0:
                return [(i, 0.0) for i in range(min(top_k, len(candidate_embeddings)))]

            similarities = np.dot(candidate_embeddings, query_embedding) / (norms * query_norm)

        # Get top k indices
        top_indices = np.argsort(similarities)[::-1][:top_k]

        # Return (index, similarity) pairs
        return [(int(idx), float(similarities[idx])) for idx in top_indices]

    def get_embedding_dimension(self) -> int:
        """Get the dimension of embeddings from this model"""
        return self.model.get_sentence_embedding_dimension()

    def get_metrics(self) -> dict:
        """Get embedding generation metrics"""

        avg_time = self.total_time / max(self.total_embeddings, 1)

        return {
            "model_name": self.config.model_name,
            "embedding_dimension": self.get_embedding_dimension(),
            "total_embeddings": self.total_embeddings,
            "total_time_seconds": self.total_time,
            "avg_time_per_embedding": avg_time,
            "embeddings_per_second": 1.0 / avg_time if avg_time > 0 else 0
        }

    def reset_metrics(self):
        """Reset metrics counters"""
        self.total_embeddings = 0
        self.total_time = 0.0


class EmbeddingError(Exception):
    """Custom exception for embedding errors"""
    pass


# Factory function

def create_embedding_generator(
    model_name: str = "all-MiniLM-L6-v2",
    device: str = "cpu",
    **kwargs
) -> EmbeddingGenerator:
    """
    Create embedding generator with simple configuration

    Args:
        model_name: Name of sentence-transformers model
        device: Device to use ("cpu" or "cuda")
        **kwargs: Additional config parameters

    Returns:
        Initialized EmbeddingGenerator

    Example:
        # Fast, lightweight model (default)
        generator = create_embedding_generator()

        # Higher quality model
        generator = create_embedding_generator(
            model_name="all-mpnet-base-v2",
            device="cuda"
        )
    """

    config = EmbeddingConfig(
        model_name=model_name,
        device=device,
        **kwargs
    )

    return EmbeddingGenerator(config)


# Convenience function for quick embeddings

_default_generator: Optional[EmbeddingGenerator] = None


def get_default_generator() -> EmbeddingGenerator:
    """Get or create default embedding generator (singleton)"""
    global _default_generator

    if _default_generator is None:
        _default_generator = create_embedding_generator()

    return _default_generator


def embed_text(text: Union[str, List[str]]) -> np.ndarray:
    """
    Quick embedding generation using default generator

    Args:
        text: Single text or list of texts

    Returns:
        Embedding(s) as numpy array
    """

    generator = get_default_generator()
    return generator.embed(text)
