"""Google Gemini embeddings utility for generating vector representations of text."""

import os
from typing import List
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()


class EmbeddingsGenerator:
    """Wrapper for Google Gemini embeddings API."""

    def __init__(self):
        """Initialize Gemini client with API key."""
        self.api_key = os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY environment variable is not set")

        self.model = os.getenv("GEMINI_EMBEDDING_MODEL", "models/text-embedding-004")
        self.client = genai.Client(api_key=self.api_key)

    async def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding vector for a single text.

        Args:
            text: Input text to embed

        Returns:
            Embedding vector (768 dimensions for text-embedding-004)

        Raises:
            ValueError: If text is empty
            Exception: If Gemini API call fails
        """
        if not text or not text.strip():
            raise ValueError("Text cannot be empty")

        result = self.client.models.embed_content(
            model=self.model,
            contents=text.strip()
        )

        return result.embeddings[0].values

    async def generate_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple texts in a single API call.

        Args:
            texts: List of input texts (max 2048 texts per batch)

        Returns:
            List of embedding vectors

        Raises:
            ValueError: If texts list is empty or exceeds batch size
        """
        if not texts:
            raise ValueError("Texts list cannot be empty")

        if len(texts) > 2048:
            raise ValueError("Maximum batch size is 2048 texts")

        # Filter out empty texts
        filtered_texts = [text.strip() for text in texts if text and text.strip()]

        if not filtered_texts:
            raise ValueError("No valid texts after filtering empty strings")

        # Process in batches
        embeddings = []
        for text in filtered_texts:
            result = self.client.models.embed_content(
                model=self.model,
                contents=text
            )
            embeddings.append(result.embeddings[0].values)

        return embeddings

    def chunk_text(
        self,
        text: str,
        chunk_size: int = 1000,
        overlap: int = 200,
    ) -> List[str]:
        """
        Split text into overlapping chunks for embedding.

        Args:
            text: Input text to chunk
            chunk_size: Maximum characters per chunk
            overlap: Number of characters to overlap between chunks

        Returns:
            List of text chunks
        """
        if not text or not text.strip():
            return []

        text = text.strip()
        chunks = []
        start = 0

        while start < len(text):
            end = start + chunk_size
            chunk = text[start:end]

            # Try to break at sentence boundary
            if end < len(text):
                last_period = chunk.rfind(". ")
                if last_period > chunk_size // 2:  # Only break if reasonably far into chunk
                    chunk = chunk[: last_period + 1]
                    end = start + len(chunk)

            chunks.append(chunk.strip())
            start = end - overlap

        return chunks


# Global instance
embeddings_generator = EmbeddingsGenerator()
