"""
Quiz Generation Service.

Generates quiz questions from chapter content using Google Gemini:
- Analyzes chapter learning objectives
- Creates diverse question types
- Adjusts difficulty based on user level
- Provides detailed explanations
"""

import json
import os
from typing import List, Dict, Any
from google import genai
from google.genai import types
from dotenv import load_dotenv

from src.models.quiz import QuestionType, Difficulty
from src.models.user_profile import SkillLevel

load_dotenv()


class QuizService:
    """
    Service for generating and managing quizzes.

    Uses Google Gemini to generate questions from chapter content.
    """

    def __init__(self):
        """Initialize quiz service with Gemini."""
        self.client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
        self.model_name = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
        self.temperature = 0.7  # Creative but consistent question generation
        self.max_tokens = 8000  # Increased for complete JSON responses

        self.generation_prompt = """You are an expert educational assessment creator for robotics and AI content.

Your task: Generate quiz questions from chapter content that test understanding and application.

Question Requirements:
1. **Alignment**: Questions must align with chapter learning objectives
2. **Variety**: Mix question types (multiple choice, true/false, code completion)
3. **Difficulty**: Adjust based on target skill level
4. **Clarity**: Questions must be unambiguous
5. **Explanations**: Provide detailed explanations for correct answers

Question Types:
- **multiple_choice**: 4 options, 1 correct (test conceptual understanding)
- **true_false**: Binary choice (test factual knowledge)
- **code_completion**: Fill in missing code (test practical application)

Output Format (JSON):
{
  "questions": [
    {
      "question_text": "What is the primary purpose of ROS 2 topics?",
      "question_type": "multiple_choice",
      "options": ["Option A", "Option B", "Option C", "Option D"],
      "correct_answer": "Option A",
      "explanation": "Detailed explanation of why this is correct and why others are wrong.",
      "difficulty": "intermediate",
      "points": 1
    },
    ...
  ]
}

Difficulty Guidelines:
- **beginner**: Basic concepts, definitions, direct recall
- **intermediate**: Application, comparison, analysis
- **advanced**: Optimization, edge cases, system design"""

    async def generate_quiz(
        self,
        chapter_content: str,
        chapter_title: str,
        learning_objectives: List[str],
        num_questions: int = 8,
        difficulty: Difficulty = Difficulty.INTERMEDIATE
    ) -> List[Dict[str, Any]]:
        """
        Generate quiz questions from chapter content.

        Args:
            chapter_content: Full chapter markdown content
            chapter_title: Chapter title
            learning_objectives: List of learning objectives
            num_questions: Number of questions to generate
            difficulty: Target difficulty level

        Returns:
            List of question dictionaries
        """
        # Build prompt with content summary
        content_summary = chapter_content[:3000]  # First 3000 chars for context
        objectives_text = "\n".join([f"- {obj}" for obj in learning_objectives])

        # Build prompt for Gemini
        prompt = f"""{self.generation_prompt}

Generate {num_questions} quiz questions for this chapter.

Chapter: {chapter_title}

Learning Objectives:
{objectives_text}

Content Preview:
{content_summary}

Target Difficulty: {difficulty.value}

Requirements:
- Generate {num_questions} questions
- Mix question types (at least 2 multiple choice, 1 true/false, 1 code completion if applicable)
- Align questions with learning objectives
- Target difficulty: {difficulty.value}
- Provide detailed explanations

Output as valid JSON following the format specified."""

        # Generate questions with Gemini
        response = self.client.models.generate_content(
            model=self.model_name,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=self.temperature,
                max_output_tokens=self.max_tokens
            )
        )
        content = response.text

        # Parse JSON response
        try:
            # Extract JSON from response (handle markdown code blocks)
            # Look for the last ``` which closes the JSON block
            if "```json" in content:
                json_start = content.find("```json") + 7
                # Find the closing ``` by looking for it at the end of the response
                json_end = content.rfind("```")
                if json_end > json_start:
                    json_str = content[json_start:json_end].strip()
                else:
                    json_str = content[json_start:].strip()
            elif content.strip().startswith("{"):
                # Direct JSON without markdown
                json_str = content.strip()
            else:
                # Try to find JSON object in response
                brace_start = content.find("{")
                brace_end = content.rfind("}") + 1
                if brace_start != -1 and brace_end > brace_start:
                    json_str = content[brace_start:brace_end]
                else:
                    json_str = content.strip()

            data = json.loads(json_str)
            questions = data.get("questions", [])

            # Add order_index to each question
            for i, question in enumerate(questions):
                question["order_index"] = i

            return questions
        except json.JSONDecodeError as e:
            # Fallback: return empty list with error logged
            print(f"Failed to parse quiz JSON: {e}")
            print(f"Response: {content}")
            return []

    def adjust_difficulty_for_user(
        self,
        questions: List[Dict[str, Any]],
        user_skill: SkillLevel
    ) -> List[Dict[str, Any]]:
        """
        Filter/adjust questions based on user skill level.

        Args:
            questions: List of all questions
            user_skill: User's skill level

        Returns:
            Filtered list of questions appropriate for user
        """
        if user_skill == SkillLevel.BEGINNER:
            # Exclude advanced questions
            return [q for q in questions if q.get("difficulty") != "advanced"]
        elif user_skill == SkillLevel.ADVANCED:
            # Exclude beginner questions
            return [q for q in questions if q.get("difficulty") != "beginner"]
        else:
            # Intermediate: include all
            return questions


# Global instance
quiz_service = QuizService()
