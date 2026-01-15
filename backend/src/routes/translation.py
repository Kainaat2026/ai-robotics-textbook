"""Translation API endpoints - DEMO VERSION (NO DATABASE)."""

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
from enum import Enum

from src.services.translation_service import translation_service

router = APIRouter()


class TargetLanguage(str, Enum):
    """Supported target languages."""
    URDU = "ur"
    ENGLISH = "en"


class TranslateRequest(BaseModel):
    """Request to translate content."""
    content: str = Field(..., min_length=10, max_length=50000)
    target_language: TargetLanguage = TargetLanguage.URDU
    content_type: str = Field(default="chapter", max_length=50)


class TranslateResponse(BaseModel):
    """Translation response."""
    translated_content: str
    source_language: str
    target_language: str
    cached: bool
    response_time_ms: int

    class Config:
        json_schema_extra = {
            "example": {
                "translated_content": "# ROS 2 موضوعات\n\nموضوعات غیر مطابقت پذیر رابطے کو فعال کرتے ہیں...",
                "source_language": "en",
                "target_language": "ur",
                "cached": False,
                "response_time_ms": 4200
            }
        }


@router.post("/translate", response_model=TranslateResponse)
async def translate_content(
    request: TranslateRequest
) -> TranslateResponse:
    """
    Translate content to target language - DEMO VERSION (NO DATABASE).

    Args:
        request: Translation request

    Returns:
        Translated content

    Example:
        POST /api/translate
        {
            "content": "## ROS 2 Topics\n\nTopics enable...",
            "target_language": "ur",
            "content_type": "chapter"
        }
    """
    # Only support English to Urdu for now
    if request.target_language != TargetLanguage.URDU:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Currently only English to Urdu translation is supported"
        )

    source_language = "en"

    # Translate content using GPT-4 (no database caching for demo)
    translated_content, response_time_ms = await translation_service.translate_to_urdu(
        content=request.content,
        content_type=request.content_type
    )

    return TranslateResponse(
        translated_content=translated_content,
        source_language=source_language,
        target_language=request.target_language.value,
        cached=False,
        response_time_ms=response_time_ms
    )
