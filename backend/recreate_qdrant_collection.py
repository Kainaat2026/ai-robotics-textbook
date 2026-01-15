"""Recreate Qdrant collection with correct dimensions for Gemini."""
import asyncio
from src.utils.vector_store import vector_store

async def recreate_collection():
    """Delete and recreate collection with 768 dimensions for Gemini."""
    try:
        print("Deleting existing collection...")
        vector_store.client.delete_collection('textbook_embeddings')
        print("Collection deleted.")
    except Exception as e:
        print(f"Collection may not exist: {e}")

    print("Creating new collection with 768 dimensions (Gemini text-embedding-004)...")
    await vector_store.create_collection(vector_size=768)
    print("Collection created successfully!")

if __name__ == "__main__":
    asyncio.run(recreate_collection())
