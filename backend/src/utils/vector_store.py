"""Qdrant vector store client wrapper for RAG functionality."""

import os
from typing import List, Dict, Any, Optional
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct, Filter, FieldCondition, MatchValue
from dotenv import load_dotenv

load_dotenv()


class VectorStore:
    """Wrapper for Qdrant vector database operations."""

    def __init__(self):
        """Initialize Qdrant client with environment configuration."""
        self.url = os.getenv("QDRANT_URL")
        self.api_key = os.getenv("QDRANT_API_KEY")
        self.collection_name = os.getenv("QDRANT_COLLECTION_NAME", "textbook_embeddings")

        if not self.url or not self.api_key:
            raise ValueError("QDRANT_URL and QDRANT_API_KEY must be set in environment")

        self.client = QdrantClient(
            url=self.url,
            api_key=self.api_key,
        )

    async def create_collection(self, vector_size: int = 1536, distance: Distance = Distance.COSINE):
        """
        Create a new collection in Qdrant.

        Args:
            vector_size: Dimension of embedding vectors (default: 1536 for text-embedding-3-small)
            distance: Distance metric (default: COSINE)
        """
        try:
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(size=vector_size, distance=distance),
            )
        except Exception as e:
            if "already exists" not in str(e).lower():
                raise

    async def upsert_vectors(
        self,
        vectors: List[List[float]],
        payloads: List[Dict[str, Any]],
        ids: Optional[List[str]] = None,
    ):
        """
        Insert or update vectors in the collection.

        Args:
            vectors: List of embedding vectors
            payloads: List of metadata dictionaries (must include 'chapter_id', 'content', 'chunk_index')
            ids: Optional list of point IDs (auto-generated if not provided)
        """
        if len(vectors) != len(payloads):
            raise ValueError("Number of vectors must match number of payloads")

        if ids and len(ids) != len(vectors):
            raise ValueError("Number of IDs must match number of vectors")

        # Generate UUID-based IDs from string IDs
        import hashlib
        import uuid

        points = []
        for i in range(len(vectors)):
            if ids:
                point_id = ids[i]
            else:
                # Generate deterministic UUID from chapter_id and chunk_index
                id_string = f"{payloads[i]['chapter_id']}_chunk_{payloads[i]['chunk_index']}"
                # Create UUID5 from the string (deterministic)
                point_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, id_string))

            points.append(PointStruct(
                id=point_id,
                vector=vectors[i],
                payload=payloads[i],
            ))

        self.client.upsert(collection_name=self.collection_name, points=points)

    async def search(
        self,
        query_vector: List[float],
        limit: int = 5,
        score_threshold: float = 0.7,
        chapter_filter: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Search for similar vectors in the collection.

        Args:
            query_vector: Query embedding vector
            limit: Maximum number of results to return
            score_threshold: Minimum similarity score (0-1)
            chapter_filter: Optional chapter ID to filter results

        Returns:
            List of search results with payload and score
        """
        search_filter = None
        if chapter_filter:
            search_filter = Filter(
                must=[FieldCondition(key="chapter_id", match=MatchValue(value=chapter_filter))]
            )

        results = self.client.query_points(
            collection_name=self.collection_name,
            query=query_vector,
            limit=limit,
            score_threshold=score_threshold,
            query_filter=search_filter,
        ).points

        return [
            {
                "id": result.id,
                "score": result.score,
                "content": result.payload.get("content", ""),
                "chapter_id": result.payload.get("chapter_id", ""),
                "chapter_title": result.payload.get("chapter_title", ""),
                "chunk_index": result.payload.get("chunk_index", 0),
            }
            for result in results
        ]

    async def delete_by_chapter(self, chapter_id: str):
        """
        Delete all vectors for a specific chapter.

        Args:
            chapter_id: Chapter identifier
        """
        self.client.delete(
            collection_name=self.collection_name,
            points_selector=Filter(
                must=[FieldCondition(key="chapter_id", match=MatchValue(value=chapter_id))]
            ),
        )

    def get_collection_info(self) -> Dict[str, Any]:
        """Get information about the collection."""
        return self.client.get_collection(collection_name=self.collection_name)


# Global instance
vector_store = VectorStore()
