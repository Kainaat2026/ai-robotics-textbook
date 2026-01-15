"""Chat conversation repository for async database operations."""

import uuid
from typing import List, Optional
from datetime import datetime
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.models.chat import ChatConversation, ChatMessage, Language, MessageRole


class ChatRepository:
    """Repository for chat conversation database operations."""

    def __init__(self, db: AsyncSession):
        """
        Initialize repository with database session.

        Args:
            db: Async database session
        """
        self.db = db

    async def create_conversation(
        self,
        user_id: Optional[uuid.UUID] = None,
        language: Language = Language.ENGLISH
    ) -> ChatConversation:
        """
        Create a new conversation.

        Args:
            user_id: User ID (nullable for anonymous users)
            language: Conversation language

        Returns:
            Created conversation
        """
        conversation = ChatConversation(
            user_id=user_id,
            language=language
        )

        self.db.add(conversation)
        await self.db.commit()
        await self.db.refresh(conversation)

        return conversation

    async def get_conversation(
        self,
        conversation_id: uuid.UUID,
        load_messages: bool = True
    ) -> Optional[ChatConversation]:
        """
        Get conversation by ID.

        Args:
            conversation_id: Conversation ID
            load_messages: Whether to load messages

        Returns:
            Conversation or None if not found
        """
        query = select(ChatConversation).where(ChatConversation.id == conversation_id)

        if load_messages:
            query = query.options(selectinload(ChatConversation.messages))

        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def add_message(
        self,
        conversation_id: uuid.UUID,
        role: MessageRole,
        message: str,
        citations: Optional[List[dict]] = None,
        tokens_used: Optional[int] = None
    ) -> ChatMessage:
        """
        Add message to conversation.

        Args:
            conversation_id: Conversation ID
            role: Message role (user or assistant)
            message: Message text
            citations: Optional list of citations
            tokens_used: Token count for cost tracking

        Returns:
            Created message
        """
        chat_message = ChatMessage(
            conversation_id=conversation_id,
            role=role,
            message=message,
            citations=citations,
            tokens_used=tokens_used
        )

        self.db.add(chat_message)

        # Update conversation timestamp
        conversation = await self.get_conversation(conversation_id, load_messages=False)
        if conversation:
            conversation.updated_at = datetime.utcnow()

        await self.db.commit()
        await self.db.refresh(chat_message)

        return chat_message

    async def get_conversation_messages(
        self,
        conversation_id: uuid.UUID,
        limit: Optional[int] = None
    ) -> List[ChatMessage]:
        """
        Get messages for a conversation.

        Args:
            conversation_id: Conversation ID
            limit: Optional limit on number of messages

        Returns:
            List of messages ordered by creation time
        """
        query = select(ChatMessage).where(
            ChatMessage.conversation_id == conversation_id
        ).order_by(ChatMessage.created_at.asc())

        if limit:
            query = query.limit(limit)

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_user_conversations(
        self,
        user_id: uuid.UUID,
        limit: int = 10
    ) -> List[ChatConversation]:
        """
        Get recent conversations for a user.

        Args:
            user_id: User ID
            limit: Number of conversations to retrieve

        Returns:
            List of conversations ordered by updated_at desc
        """
        query = select(ChatConversation).where(
            ChatConversation.user_id == user_id
        ).order_by(desc(ChatConversation.updated_at)).limit(limit)

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def delete_conversation(self, conversation_id: uuid.UUID) -> bool:
        """
        Delete a conversation and all its messages.

        Args:
            conversation_id: Conversation ID

        Returns:
            True if deleted, False if not found
        """
        conversation = await self.get_conversation(conversation_id, load_messages=False)

        if not conversation:
            return False

        await self.db.delete(conversation)
        await self.db.commit()

        return True

    async def get_conversation_history_for_rag(
        self,
        conversation_id: uuid.UUID,
        last_n: int = 6
    ) -> List[dict]:
        """
        Get conversation history formatted for RAG service.

        Args:
            conversation_id: Conversation ID
            last_n: Number of recent messages (default 6 = 3 exchanges)

        Returns:
            List of dicts with 'role' and 'content' keys
        """
        messages = await self.get_conversation_messages(conversation_id)

        # Get last N messages
        recent_messages = messages[-last_n:] if len(messages) > last_n else messages

        # Format for RAG service
        return [
            {
                'role': msg.role.value,
                'content': msg.message
            }
            for msg in recent_messages
        ]
