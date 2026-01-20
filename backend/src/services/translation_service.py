"""
Translation Service for Urdu Language Support.

Translates textbook content to Urdu while preserving:
- Markdown structure
- Code blocks (kept in English)
- Technical terms (transliterated appropriately)
- Diagram references
"""

import time
import hashlib
import os
from typing import Tuple, Optional
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()


class TranslationService:
    """
    Service for translating textbook content to Urdu.

    Uses Google Gemini with specialized Urdu translation prompts:
    - Preserves code blocks in English
    - Handles technical term transliteration
    - Maintains markdown structure
    - Ensures RTL compatibility
    """

    def __init__(self):
        """Initialize translation service with Gemini."""
        # Support both GOOGLE_API_KEY and GEMINI_API_KEY for flexibility
        api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
        self.client = genai.Client(api_key=api_key)
        self.model_name = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
        self.temperature = 0.2  # Low temperature for consistent translations
        self.max_tokens = 4000

        # Urdu translation system prompt
        self.urdu_prompt = """You are an expert technical translator specializing in translating robotics and AI content from English to Urdu.

Translation Guidelines:

1. **Text Content**: Translate all headings, paragraphs, and explanations to natural, fluent Urdu
2. **Code Blocks**: Keep ALL code in English (Python, ROS 2, bash, etc.)
3. **Technical Terms**:
   - Use established Urdu computing terms where available
   - Transliterate English terms when no equivalent exists (Robot → روبوٹ, Simulation → سمولیشن)
   - Keep acronyms in English: ROS 2, AI, ML, GPU, CUDA
4. **Markdown Structure**: Preserve ALL markdown formatting (headings, lists, code blocks, links, images)
5. **Code Comments**: Translate comments inside code blocks to Urdu
6. **URLs and Links**: Keep URLs in English, translate link text to Urdu
7. **Technical Accuracy**: Ensure translations are technically accurate and clear

Examples:
- "Robot Operating System" → "روبوٹ آپریٹنگ سسٹم (Robot Operating System)"
- "Publisher-Subscriber Pattern" → "پبلشر-سبسکرائبر پیٹرن"
- "URDF format" → "URDF فارمیٹ"

Output: Provide ONLY the translated content in proper Urdu with correct RTL text direction markers."""

    async def translate_to_urdu(
        self,
        content: str,
        content_type: str = "chapter"
    ) -> Tuple[str, int]:
        """
        Translate content to Urdu.

        Args:
            content: Original English markdown content
            content_type: Type of content (chapter, section, etc.)

        Returns:
            Tuple of (translated_content, response_time_ms)
        """
        start_time = time.time()

        # Build translation prompt with system instruction
        user_prompt = f"""Translate the following {content_type} content to Urdu:

{content}

Remember: Translate text to Urdu, keep code in English, preserve markdown structure."""

        # Generate translation with Gemini
        response = self.client.models.generate_content(
            model=self.model_name,
            contents=user_prompt,
            config=types.GenerateContentConfig(
                temperature=self.temperature,
                max_output_tokens=self.max_tokens,
                system_instruction=self.urdu_prompt
            )
        )

        translated_content = response.text

        response_time_ms = int((time.time() - start_time) * 1000)

        return translated_content, response_time_ms

    @staticmethod
    def generate_content_hash(content: str) -> str:
        """
        Generate hash for caching translations.

        Args:
            content: Content to hash

        Returns:
            SHA-256 hash of content
        """
        return hashlib.sha256(content.encode('utf-8')).hexdigest()


# Global instance
translation_service = TranslationService()
