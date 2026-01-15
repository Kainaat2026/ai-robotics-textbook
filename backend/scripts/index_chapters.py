"""
Chapter Indexing Script for RAG System.

This script:
1. Reads markdown chapter files from docs/ directory
2. Extracts frontmatter metadata
3. Chunks content into ~500-token segments
4. Generates embeddings using OpenAI
5. Uploads to Qdrant vector store

Usage:
    python scripts/index_chapters.py --docs-dir ../frontend/docs --all
    python scripts/index_chapters.py --chapter chapter-03-ros2-topics
"""

import asyncio
import argparse
import os
import sys
from pathlib import Path
from typing import List, Dict, Any
import re
import frontmatter

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.models.chapter import ChapterMetadata, ChapterChunk
from src.utils.embeddings import embeddings_generator
from src.utils.vector_store import vector_store


class ChapterIndexer:
    """Handles chapter indexing workflow."""

    def __init__(self, docs_dir: str):
        """
        Initialize indexer.

        Args:
            docs_dir: Path to docs directory containing markdown files
        """
        self.docs_dir = Path(docs_dir)
        if not self.docs_dir.exists():
            raise ValueError(f"Docs directory not found: {docs_dir}")

    def find_chapters(self) -> List[Path]:
        """
        Find all chapter markdown files.

        Returns:
            List of Path objects for chapter files
        """
        chapters = []
        for module_dir in self.docs_dir.glob("module-*"):
            if module_dir.is_dir():
                chapters.extend(module_dir.glob("chapter-*.md"))

        return sorted(chapters)

    def parse_chapter(self, file_path: Path) -> Dict[str, Any]:
        """
        Parse chapter markdown file and extract metadata.

        Args:
            file_path: Path to chapter markdown file

        Returns:
            Dict with 'metadata' and 'content' keys
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            post = frontmatter.load(f)

        # Extract metadata from frontmatter
        metadata = ChapterMetadata(
            id=post.get('id', file_path.stem),
            title=post.get('title', ''),
            module=post.get('module', 1),
            week=post.get('week', 1),
            learning_objectives=post.get('learning_objectives', []),
            estimated_time_minutes=post.get('estimated_time_minutes', 30)
        )

        return {
            'metadata': metadata,
            'content': post.content,
            'file_path': str(file_path)
        }

    def extract_sections(self, content: str) -> List[Dict[str, str]]:
        """
        Extract sections from markdown content.

        Args:
            content: Markdown content

        Returns:
            List of dicts with 'heading' and 'content'
        """
        # Split by ## headings (level 2), but ignore headings inside code blocks
        sections = []
        lines = content.split('\n')
        current_section = None
        current_content = []
        in_code_block = False

        for line in lines:
            # Track code block boundaries
            if line.strip().startswith('```'):
                in_code_block = not in_code_block
                current_content.append(line)
            elif line.startswith('## ') and not in_code_block:
                # Save previous section
                if current_section:
                    sections.append({
                        'heading': current_section,
                        'content': '\n'.join(current_content).strip()
                    })
                # Start new section
                current_section = line.replace('## ', '').strip()
                current_content = []
            else:
                current_content.append(line)

        # Save last section
        if current_section:
            sections.append({
                'heading': current_section,
                'content': '\n'.join(current_content).strip()
            })

        return sections

    def chunk_content(self, metadata: ChapterMetadata, content: str, chunk_size: int = 1000, overlap: int = 200) -> List[ChapterChunk]:
        """
        Chunk chapter content with overlap.

        Args:
            metadata: Chapter metadata
            content: Full chapter content
            chunk_size: Target characters per chunk
            overlap: Overlap characters between chunks

        Returns:
            List of ChapterChunk objects
        """
        chunks = []
        sections = self.extract_sections(content)

        chunk_index = 0
        for section in sections:
            section_content = section['content']
            section_heading = section['heading']

            # Skip sections that are too short (< 50 chars minimum for validation)
            if len(section_content) < 50:
                continue

            # Chunk large sections
            if len(section_content) <= chunk_size:
                # Section fits in one chunk
                chunks.append(ChapterChunk(
                    chapter_id=metadata.id,
                    chunk_index=chunk_index,
                    content=section_content,
                    section_heading=section_heading,
                    chapter_title=metadata.title,
                    module=metadata.module
                ))
                chunk_index += 1
            else:
                # Split large section into chunks
                text_chunks = embeddings_generator.chunk_text(
                    section_content,
                    chunk_size=chunk_size,
                    overlap=overlap
                )

                for text_chunk in text_chunks:
                    # Skip chunks that are too short
                    if len(text_chunk) < 50:
                        continue

                    chunks.append(ChapterChunk(
                        chapter_id=metadata.id,
                        chunk_index=chunk_index,
                        content=text_chunk,
                        section_heading=section_heading,
                        chapter_title=metadata.title,
                        module=metadata.module
                    ))
                    chunk_index += 1

        return chunks

    async def index_chapter(self, file_path: Path) -> int:
        """
        Index a single chapter to Qdrant.

        Args:
            file_path: Path to chapter markdown file

        Returns:
            Number of chunks indexed
        """
        print(f"Indexing: {file_path.name}")

        # Parse chapter
        chapter_data = self.parse_chapter(file_path)
        metadata = chapter_data['metadata']
        content = chapter_data['content']

        # Chunk content
        chunks = self.chunk_content(metadata, content)
        print(f"  Created {len(chunks)} chunks")

        if not chunks:
            print(f"  Warning: No chunks created for {file_path.name}")
            return 0

        # Generate embeddings
        chunk_texts = [chunk.content for chunk in chunks]
        print(f"  Generating embeddings...")
        embeddings = await embeddings_generator.generate_embeddings_batch(chunk_texts)
        print(f"  Generated {len(embeddings)} embeddings")

        # Prepare payloads for Qdrant
        payloads = [
            {
                'chapter_id': chunk.chapter_id,
                'chunk_index': chunk.chunk_index,
                'content': chunk.content,
                'section_heading': chunk.section_heading,
                'chapter_title': chunk.chapter_title,
                'module': chunk.module
            }
            for chunk in chunks
        ]

        # Upload to Qdrant
        print(f"  Uploading to Qdrant...")
        await vector_store.upsert_vectors(
            vectors=embeddings,
            payloads=payloads
        )
        print(f"  OK Indexed {len(chunks)} chunks for {metadata.title}")

        return len(chunks)

    async def index_all(self) -> Dict[str, int]:
        """
        Index all chapters in docs directory.

        Returns:
            Dict mapping chapter_id to chunk count
        """
        chapters = self.find_chapters()

        if not chapters:
            print("No chapter files found!")
            return {}

        print(f"Found {len(chapters)} chapters to index\n")

        # Ensure collection exists
        try:
            await vector_store.create_collection()
            print("OK Qdrant collection ready\n")
        except Exception as e:
            print(f"Note: {e}\n")

        results = {}
        for chapter_file in chapters:
            try:
                chunk_count = await self.index_chapter(chapter_file)
                results[chapter_file.stem] = chunk_count
            except Exception as e:
                print(f"  ERROR Error indexing {chapter_file.name}: {e}")
                results[chapter_file.stem] = 0

        return results


async def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Index textbook chapters for RAG")
    parser.add_argument('--docs-dir', default='../frontend/docs', help='Path to docs directory')
    parser.add_argument('--chapter', help='Index specific chapter by ID')
    parser.add_argument('--all', action='store_true', help='Index all chapters')

    args = parser.parse_args()

    indexer = ChapterIndexer(args.docs_dir)

    if args.all:
        print("=== Indexing All Chapters ===\n")
        results = await indexer.index_all()

        print("\n=== Summary ===")
        total_chunks = sum(results.values())
        print(f"Total chapters: {len(results)}")
        print(f"Total chunks: {total_chunks}")
        print(f"Average chunks per chapter: {total_chunks / len(results) if results else 0:.1f}")

    elif args.chapter:
        # Find specific chapter file
        chapter_files = indexer.find_chapters()
        target_file = None
        for f in chapter_files:
            if args.chapter in f.stem:
                target_file = f
                break

        if target_file:
            chunk_count = await indexer.index_chapter(target_file)
            print(f"\nOK Indexed {chunk_count} chunks")
        else:
            print(f"Chapter not found: {args.chapter}")
            return 1
    else:
        parser.print_help()
        return 1

    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
