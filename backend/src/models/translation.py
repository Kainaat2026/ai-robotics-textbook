"""Translation models for database caching."""

from datetime import datetime
from sqlalchemy import Column, String, DateTime, Text, Index
from sqlalchemy.dialects.postgresql import UUID
import uuid

from src.db.connection import Base


class Translation(Base):
    """
    Cached translation for content.

    Stores translations to avoid re-translating the same content.

    Attributes:
        id: Unique translation identifier
        content_hash: SHA-256 hash of source content
        source_language: Source language code (en)
        target_language: Target language code (ur)
        source_content: Original content (for reference)
        translated_content: Translated text
        content_type: Type of content (chapter, section, etc.)
        created_at: Translation timestamp
    """
    __tablename__ = "translations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    content_hash = Column(String(64), nullable=False, index=True)
    source_language = Column(String(5), nullable=False, default="en")
    target_language = Column(String(5), nullable=False)
    source_content = Column(Text, nullable=False)
    translated_content = Column(Text, nullable=False)
    content_type = Column(String(50), nullable=True)  # chapter, section, etc.
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    # Composite index for fast lookups
    __table_args__ = (
        Index('idx_translation_lookup', 'content_hash', 'source_language', 'target_language'),
    )

    def __repr__(self):
        return f"<Translation(hash={self.content_hash[:8]}, {self.source_language}→{self.target_language})>"
