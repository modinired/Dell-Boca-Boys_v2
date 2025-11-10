"""
ChromaDB Memory Store
Persistent vector database for semantic memory
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from pathlib import Path
import uuid

import chromadb
from chromadb.config import Settings
from chromadb.utils import embedding_functions

from .embeddings import EmbeddingGenerator

logger = logging.getLogger(__name__)


class ChromaMemoryStore:
    """
    Persistent memory storage using ChromaDB

    Stores conversation history, learned information, and user context
    with semantic search capabilities for RAG
    """

    def __init__(
        self,
        persist_directory: str,
        collection_name: str = "spedines_memory",
        embedding_generator: Optional[EmbeddingGenerator] = None
    ):
        """
        Initialize ChromaDB memory store

        Args:
            persist_directory: Directory to persist ChromaDB data
            collection_name: Name of collection to use
            embedding_generator: Optional custom embedding generator
        """

        self.persist_directory = Path(persist_directory)
        self.collection_name = collection_name

        # Create directory if needed
        self.persist_directory.mkdir(parents=True, exist_ok=True)

        logger.info(f"Initializing ChromaDB at {self.persist_directory}")

        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(
            path=str(self.persist_directory),
            settings=Settings(
                anonymized_telemetry=False,  # Disable telemetry for privacy
                allow_reset=True
            )
        )

        # Set up embedding function
        if embedding_generator:
            self.embedding_generator = embedding_generator
            # Create custom embedding function for Chroma
            self.embedding_function = self._create_custom_embedding_function(
                embedding_generator
            )
        else:
            # Use Chroma's default embedding function
            self.embedding_function = embedding_functions.DefaultEmbeddingFunction()
            self.embedding_generator = None

        # Get or create collection
        try:
            self.collection = self.client.get_collection(
                name=collection_name,
                embedding_function=self.embedding_function
            )
            logger.info(f"Loaded existing collection '{collection_name}' with {self.collection.count()} items")

        except Exception:
            # Collection doesn't exist, create it
            self.collection = self.client.create_collection(
                name=collection_name,
                embedding_function=self.embedding_function,
                metadata={"description": "Spedines agent persistent memory"}
            )
            logger.info(f"Created new collection '{collection_name}'")

        # Metrics
        self.memories_added = 0
        self.queries_performed = 0

    def _create_custom_embedding_function(self, generator: EmbeddingGenerator):
        """Create custom embedding function for ChromaDB using our generator"""

        class CustomEmbeddingFunction:
            def __init__(self, generator):
                self.generator = generator

            def __call__(self, input: List[str]) -> List[List[float]]:
                """Generate embeddings for list of texts"""
                embeddings = self.generator.embed(input)
                # Convert to list of lists
                return embeddings.tolist()

        return CustomEmbeddingFunction(generator)

    def add_memory(
        self,
        content: str,
        metadata: Optional[Dict[str, Any]] = None,
        memory_id: Optional[str] = None
    ) -> str:
        """
        Add a memory to the store

        Args:
            content: Text content of the memory
            metadata: Optional metadata (tags, source, timestamp, etc.)
            memory_id: Optional custom ID (generated if not provided)

        Returns:
            ID of the added memory
        """

        # Generate ID if not provided
        if memory_id is None:
            memory_id = str(uuid.uuid4())

        # Add timestamp to metadata if not present
        if metadata is None:
            metadata = {}

        if "timestamp" not in metadata:
            metadata["timestamp"] = datetime.now().isoformat()

        # Add to collection
        try:
            self.collection.add(
                documents=[content],
                metadatas=[metadata],
                ids=[memory_id]
            )

            self.memories_added += 1

            logger.debug(f"Added memory {memory_id}: {content[:100]}...")

            return memory_id

        except Exception as e:
            logger.error(f"Failed to add memory: {e}")
            raise MemoryError(f"Failed to add memory: {e}")

    def add_memories(
        self,
        contents: List[str],
        metadatas: Optional[List[Dict[str, Any]]] = None,
        memory_ids: Optional[List[str]] = None
    ) -> List[str]:
        """
        Add multiple memories in batch

        Args:
            contents: List of text contents
            metadatas: Optional list of metadata dicts
            memory_ids: Optional list of IDs

        Returns:
            List of IDs for added memories
        """

        if not contents:
            return []

        # Generate IDs if not provided
        if memory_ids is None:
            memory_ids = [str(uuid.uuid4()) for _ in contents]

        # Generate metadata if not provided
        if metadatas is None:
            timestamp = datetime.now().isoformat()
            metadatas = [{"timestamp": timestamp} for _ in contents]
        else:
            # Add timestamps where missing
            for metadata in metadatas:
                if "timestamp" not in metadata:
                    metadata["timestamp"] = datetime.now().isoformat()

        try:
            self.collection.add(
                documents=contents,
                metadatas=metadatas,
                ids=memory_ids
            )

            self.memories_added += len(contents)

            logger.info(f"Added {len(contents)} memories in batch")

            return memory_ids

        except Exception as e:
            logger.error(f"Failed to add memories in batch: {e}")
            raise MemoryError(f"Failed to add memories: {e}")

    def query(
        self,
        query_text: str,
        n_results: int = 5,
        where: Optional[Dict] = None,
        where_document: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Query memories using semantic search

        Args:
            query_text: Text to search for
            n_results: Number of results to return
            where: Optional metadata filter
            where_document: Optional document content filter

        Returns:
            Dictionary with ids, documents, metadatas, and distances
        """

        try:
            results = self.collection.query(
                query_texts=[query_text],
                n_results=n_results,
                where=where,
                where_document=where_document
            )

            self.queries_performed += 1

            logger.debug(f"Query returned {len(results['ids'][0])} results")

            return {
                "ids": results["ids"][0],
                "documents": results["documents"][0],
                "metadatas": results["metadatas"][0],
                "distances": results["distances"][0]
            }

        except Exception as e:
            logger.error(f"Query failed: {e}")
            raise MemoryError(f"Query failed: {e}")

    def get_memory(self, memory_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a specific memory by ID

        Args:
            memory_id: ID of memory to retrieve

        Returns:
            Dictionary with memory data or None if not found
        """

        try:
            results = self.collection.get(
                ids=[memory_id]
            )

            if not results["ids"]:
                return None

            return {
                "id": results["ids"][0],
                "document": results["documents"][0],
                "metadata": results["metadatas"][0]
            }

        except Exception as e:
            logger.error(f"Failed to get memory {memory_id}: {e}")
            return None

    def update_memory(
        self,
        memory_id: str,
        content: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Update an existing memory

        Args:
            memory_id: ID of memory to update
            content: New content (if updating)
            metadata: New metadata (if updating)

        Returns:
            True if updated successfully
        """

        try:
            update_kwargs = {"ids": [memory_id]}

            if content is not None:
                update_kwargs["documents"] = [content]

            if metadata is not None:
                # Add updated timestamp
                metadata["updated_at"] = datetime.now().isoformat()
                update_kwargs["metadatas"] = [metadata]

            self.collection.update(**update_kwargs)

            logger.debug(f"Updated memory {memory_id}")

            return True

        except Exception as e:
            logger.error(f"Failed to update memory {memory_id}: {e}")
            return False

    def delete_memory(self, memory_id: str) -> bool:
        """
        Delete a memory

        Args:
            memory_id: ID of memory to delete

        Returns:
            True if deleted successfully
        """

        try:
            self.collection.delete(ids=[memory_id])

            logger.debug(f"Deleted memory {memory_id}")

            return True

        except Exception as e:
            logger.error(f"Failed to delete memory {memory_id}: {e}")
            return False

    def delete_memories(
        self,
        where: Optional[Dict] = None,
        memory_ids: Optional[List[str]] = None
    ) -> bool:
        """
        Delete multiple memories by filter or IDs

        Args:
            where: Optional metadata filter
            memory_ids: Optional list of IDs to delete

        Returns:
            True if deleted successfully
        """

        try:
            delete_kwargs = {}

            if memory_ids:
                delete_kwargs["ids"] = memory_ids
            elif where:
                delete_kwargs["where"] = where
            else:
                raise ValueError("Must provide either where filter or memory_ids")

            self.collection.delete(**delete_kwargs)

            logger.info(f"Deleted memories with filter")

            return True

        except Exception as e:
            logger.error(f"Failed to delete memories: {e}")
            return False

    def count(self, where: Optional[Dict] = None) -> int:
        """
        Count memories in collection

        Args:
            where: Optional metadata filter

        Returns:
            Number of memories matching filter
        """

        try:
            if where:
                results = self.collection.get(where=where)
                return len(results["ids"])
            else:
                return self.collection.count()

        except Exception as e:
            logger.error(f"Failed to count memories: {e}")
            return 0

    def search_by_metadata(
        self,
        where: Dict,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Search memories by metadata filter

        Args:
            where: Metadata filter (e.g., {"source": "conversation"})
            limit: Optional limit on results

        Returns:
            List of matching memories
        """

        try:
            results = self.collection.get(
                where=where,
                limit=limit
            )

            memories = []
            for i in range(len(results["ids"])):
                memories.append({
                    "id": results["ids"][i],
                    "document": results["documents"][i],
                    "metadata": results["metadatas"][i]
                })

            return memories

        except Exception as e:
            logger.error(f"Metadata search failed: {e}")
            return []

    def get_recent_memories(
        self,
        n: int = 10,
        source: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get most recent memories

        Args:
            n: Number of memories to retrieve
            source: Optional filter by source

        Returns:
            List of recent memories
        """

        try:
            where = {"source": source} if source else None

            results = self.collection.get(
                where=where,
                limit=n
            )

            # Sort by timestamp (newest first)
            memories = []
            for i in range(len(results["ids"])):
                memory = {
                    "id": results["ids"][i],
                    "document": results["documents"][i],
                    "metadata": results["metadatas"][i]
                }

                # Parse timestamp for sorting
                timestamp_str = memory["metadata"].get("timestamp", "")
                try:
                    memory["_timestamp"] = datetime.fromisoformat(timestamp_str)
                except Exception:
                    memory["_timestamp"] = datetime.min

                memories.append(memory)

            # Sort by timestamp descending
            memories.sort(key=lambda m: m["_timestamp"], reverse=True)

            # Remove temporary sorting key
            for memory in memories:
                del memory["_timestamp"]

            return memories[:n]

        except Exception as e:
            logger.error(f"Failed to get recent memories: {e}")
            return []

    def clear_all(self) -> bool:
        """
        Clear all memories from collection

        WARNING: This deletes all data!

        Returns:
            True if successful
        """

        try:
            # Delete collection
            self.client.delete_collection(name=self.collection_name)

            # Recreate empty collection
            self.collection = self.client.create_collection(
                name=self.collection_name,
                embedding_function=self.embedding_function,
                metadata={"description": "Spedines agent persistent memory"}
            )

            logger.warning("Cleared all memories from collection")

            return True

        except Exception as e:
            logger.error(f"Failed to clear collection: {e}")
            return False

    def get_metrics(self) -> Dict[str, Any]:
        """Get memory store metrics"""

        return {
            "collection_name": self.collection_name,
            "total_memories": self.collection.count(),
            "memories_added_this_session": self.memories_added,
            "queries_performed": self.queries_performed,
            "persist_directory": str(self.persist_directory)
        }

    def export_memories(
        self,
        output_file: str,
        where: Optional[Dict] = None
    ) -> bool:
        """
        Export memories to JSON file

        Args:
            output_file: Path to output file
            where: Optional metadata filter

        Returns:
            True if successful
        """

        import json

        try:
            # Get all matching memories
            results = self.collection.get(where=where)

            memories = []
            for i in range(len(results["ids"])):
                memories.append({
                    "id": results["ids"][i],
                    "document": results["documents"][i],
                    "metadata": results["metadatas"][i]
                })

            # Write to file
            with open(output_file, 'w') as f:
                json.dump({
                    "collection": self.collection_name,
                    "exported_at": datetime.now().isoformat(),
                    "count": len(memories),
                    "memories": memories
                }, f, indent=2)

            logger.info(f"Exported {len(memories)} memories to {output_file}")

            return True

        except Exception as e:
            logger.error(f"Failed to export memories: {e}")
            return False


class MemoryError(Exception):
    """Custom exception for memory operations"""
    pass


# Factory function

def create_memory_store(
    persist_directory: str,
    collection_name: str = "spedines_memory",
    embedding_model: str = "all-MiniLM-L6-v2"
) -> ChromaMemoryStore:
    """
    Create ChromaDB memory store with embedding generator

    Args:
        persist_directory: Directory for ChromaDB persistence
        collection_name: Name of collection
        embedding_model: Sentence-transformers model to use

    Returns:
        Initialized ChromaMemoryStore
    """

    from .embeddings import create_embedding_generator

    # Create embedding generator
    generator = create_embedding_generator(model_name=embedding_model)

    # Create memory store
    store = ChromaMemoryStore(
        persist_directory=persist_directory,
        collection_name=collection_name,
        embedding_generator=generator
    )

    return store
