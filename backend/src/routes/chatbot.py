"""Chat API endpoints for RAG chatbot."""

import uuid
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.connection import get_db
from src.db.repositories.chat_repo import ChatRepository
from src.models.chat import (
    ChatMessageCreate,
    ChatMessageResponse,
    ConversationHistoryResponse,
    MessageHistoryItem,
    TextSelectionRequest,
    TextSelectionResponse,
    MessageRole
)
from src.services.rag_service import rag_service

router = APIRouter()


@router.post("/chat", response_model=ChatMessageResponse, status_code=status.HTTP_200_OK)
async def send_chat_message(
    request: ChatMessageCreate,
    db: AsyncSession = Depends(get_db)
) -> ChatMessageResponse:
    """
    Send a message to the chatbot and get AI response.

    Args:
        request: Chat message request
        db: Database session

    Returns:
        Chatbot response with citations

    Example:
        POST /api/chat
        {
            "conversation_id": null,
            "message": "What are ROS 2 topics?",
            "language": "en"
        }
    """
    chat_repo = ChatRepository(db)

    # Get or create conversation
    if request.conversation_id:
        conversation = await chat_repo.get_conversation(request.conversation_id, load_messages=False)
        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Conversation {request.conversation_id} not found"
            )
    else:
        # Create new conversation
        conversation = await chat_repo.create_conversation(
            user_id=None,  # TODO: Get from auth context when Phase 6 complete
            language=request.language
        )

    # Save user message
    await chat_repo.add_message(
        conversation_id=conversation.id,
        role=MessageRole.USER,
        message=request.message
    )

    # Get conversation history for context
    conversation_history = await chat_repo.get_conversation_history_for_rag(
        conversation_id=conversation.id,
        last_n=6
    )

    # Generate AI response using RAG
    response_text, citations, tokens_used, response_time_ms = await rag_service.generate_response(
        query=request.message,
        conversation_history=conversation_history[:-1],  # Exclude the message we just added
        language=request.language
    )

    # Save assistant response
    citations_dict = [citation.model_dump() for citation in citations]
    await chat_repo.add_message(
        conversation_id=conversation.id,
        role=MessageRole.ASSISTANT,
        message=response_text,
        citations=citations_dict,
        tokens_used=tokens_used
    )

    return ChatMessageResponse(
        conversation_id=conversation.id,
        message=response_text,
        citations=citations,
        tokens_used=tokens_used,
        response_time_ms=response_time_ms
    )


@router.get("/chat/conversation/{conversation_id}", response_model=ConversationHistoryResponse)
async def get_conversation_history(
    conversation_id: uuid.UUID,
    db: AsyncSession = Depends(get_db)
) -> ConversationHistoryResponse:
    """
    Get full conversation history.

    Args:
        conversation_id: Conversation ID
        db: Database session

    Returns:
        Conversation with all messages

    Example:
        GET /api/chat/conversation/123e4567-e89b-12d3-a456-426614174000
    """
    chat_repo = ChatRepository(db)

    conversation = await chat_repo.get_conversation(conversation_id, load_messages=True)

    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Conversation {conversation_id} not found"
        )

    # Convert messages to response format
    message_items = [
        MessageHistoryItem(
            id=msg.id,
            role=msg.role,
            message=msg.message,
            citations=[citation for citation in (msg.citations or [])],
            created_at=msg.created_at
        )
        for msg in conversation.messages
    ]

    return ConversationHistoryResponse(
        conversation_id=conversation.id,
        language=conversation.language,
        messages=message_items,
        created_at=conversation.created_at,
        updated_at=conversation.updated_at
    )


@router.delete("/chat/conversation/{conversation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_conversation(
    conversation_id: uuid.UUID,
    db: AsyncSession = Depends(get_db)
):
    """
    Delete a conversation and all its messages.

    Args:
        conversation_id: Conversation ID
        db: Database session

    Returns:
        204 No Content

    Example:
        DELETE /api/chat/conversation/123e4567-e89b-12d3-a456-426614174000
    """
    chat_repo = ChatRepository(db)

    deleted = await chat_repo.delete_conversation(conversation_id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Conversation {conversation_id} not found"
        )


@router.post("/chat/text-selection", response_model=TextSelectionResponse)
async def explain_text_selection(
    request: TextSelectionRequest,
    db: AsyncSession = Depends(get_db)
) -> TextSelectionResponse:
    """
    Get AI explanation for selected text (User Story 3 - Text Selection AI).

    Args:
        request: Selected text and context
        db: Database session

    Returns:
        Contextual explanation with citations

    Example:
        POST /api/chat/text-selection
        {
            "selected_text": "URDF format",
            "chapter_id": "chapter-06-gazebo-intro",
            "surrounding_context": "Robots are described using the URDF format for simulation.",
            "language": "en"
        }
    """
    # Generate explanation using RAG service
    explanation, citations, response_time_ms = await rag_service.generate_text_selection_explanation(
        selected_text=request.selected_text,
        chapter_id=request.chapter_id,
        surrounding_context=request.surrounding_context,
        language=request.language
    )

    return TextSelectionResponse(
        explanation=explanation,
        citations=citations,
        response_time_ms=response_time_ms
    )
