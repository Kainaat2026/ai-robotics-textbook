"""Chapter entity model for textbook content metadata."""

from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class ChapterMetadata(BaseModel):
    """
    Chapter metadata extracted from markdown frontmatter.

    Attributes:
        id: Chapter identifier (e.g., "chapter-03-ros2-topics")
        title: Chapter title
        module: Module number (1-4)
        week: Week number in course (1-13)
        learning_objectives: List of 3-5 learning outcomes
        estimated_time_minutes: Estimated reading time
    """
    id: str = Field(..., max_length=100, description="Chapter slug matching filename")
    title: str = Field(..., max_length=255)
    module: int = Field(..., ge=1, le=4, description="Module number (1-4)")
    week: int = Field(..., ge=1, le=13, description="Week number in course")
    learning_objectives: List[str] = Field(..., min_items=3, max_items=5)
    estimated_time_minutes: int = Field(..., ge=5, le=120)

    class Config:
        json_schema_extra = {
            "example": {
                "id": "chapter-03-ros2-topics",
                "title": "ROS 2 Topics: Publisher-Subscriber Communication",
                "module": 1,
                "week": 3,
                "learning_objectives": [
                    "Understand publish-subscribe pattern",
                    "Create publishers and subscribers in Python",
                    "Visualize topic communication with rqt_graph"
                ],
                "estimated_time_minutes": 45
            }
        }


class ChapterContent(BaseModel):
    """
    Chapter content for processing and embedding.

    Attributes:
        metadata: Chapter metadata
        content: Full markdown content (excluding frontmatter)
        sections: List of section headings
        code_examples: Number of code examples in chapter
    """
    metadata: ChapterMetadata
    content: str = Field(..., min_length=100)
    sections: List[str] = Field(default_factory=list)
    code_examples: int = Field(0, ge=0)


class ChapterChunk(BaseModel):
    """
    Chunk of chapter content for vector embedding.

    Attributes:
        chapter_id: Reference to parent chapter
        chunk_index: Sequential index of chunk within chapter
        content: Chunk text (~500 tokens)
        section_heading: Section this chunk belongs to
        metadata: Additional metadata for retrieval
    """
    chapter_id: str = Field(..., max_length=100)
    chunk_index: int = Field(..., ge=0)
    content: str = Field(..., min_length=50, max_length=3000)
    section_heading: Optional[str] = Field(None, max_length=255)

    # Additional metadata for better retrieval
    chapter_title: str = Field(..., max_length=255)
    module: int = Field(..., ge=1, le=4)

    class Config:
        json_schema_extra = {
            "example": {
                "chapter_id": "chapter-03-ros2-topics",
                "chunk_index": 0,
                "content": "ROS 2 Topics enable asynchronous communication between nodes using a publish-subscribe pattern. Publishers send messages to topics, and subscribers receive messages from topics they're interested in.",
                "section_heading": "2.1 Publisher-Subscriber Pattern",
                "chapter_title": "ROS 2 Topics",
                "module": 1
            }
        }


class ChapterList(BaseModel):
    """List of all available chapters."""
    chapters: List[ChapterMetadata]
    total_count: int


class ChapterSearchResult(BaseModel):
    """
    Result from semantic search of chapter content.

    Attributes:
        chapter_id: Chapter containing the match
        chapter_title: Title of the chapter
        section: Section heading where match was found
        content: Matching content snippet
        score: Similarity score (0-1)
        chunk_index: Index of the chunk in the chapter
    """
    chapter_id: str
    chapter_title: str
    section: Optional[str]
    content: str
    score: float = Field(..., ge=0.0, le=1.0)
    chunk_index: int = Field(..., ge=0)

    class Config:
        json_schema_extra = {
            "example": {
                "chapter_id": "chapter-03-ros2-topics",
                "chapter_title": "ROS 2 Topics",
                "section": "2.1 Publisher-Subscriber Pattern",
                "content": "Topics use asynchronous message passing, allowing nodes to communicate without blocking.",
                "score": 0.89,
                "chunk_index": 2
            }
        }
