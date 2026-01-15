"""
Personalization Service for Content Adaptation.

Adapts textbook chapter content based on user's skill level and background:
- Beginner: More explanations, simpler examples, prerequisite links
- Intermediate: Standard content with balanced depth
- Advanced: Concise explanations, optimization focus, edge cases
"""

import time
from typing import Tuple
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage

from src.models.user import SkillLevel


class PersonalizationService:
    """
    Service for adapting textbook content to user skill levels.

    Uses OpenAI GPT-4 to rewrite chapter content based on:
    - User's skill level (beginner/intermediate/advanced)
    - Python/AI/robotics experience
    - Hardware availability (RTX GPU, Jetson, robots)
    """

    def __init__(self):
        """Initialize personalization service with GPT-4."""
        self.llm = ChatOpenAI(
            model="gpt-4-turbo",
            temperature=0.4,  # Balanced creativity for adaptation
            max_tokens=3000,  # Allow longer personalized content
        )

        # System prompts for different skill levels
        self.beginner_prompt = """You are an expert technical educator adapting robotics content for BEGINNERS.

Your task:
- Add more foundational explanations for technical concepts
- Include analogies and real-world examples
- Break down complex ideas into simpler steps
- Add prerequisite knowledge reminders
- Use encouraging, patient language
- Simplify code examples with more comments

Maintain:
- Technical accuracy
- Original markdown structure
- Code blocks (with added comments)
- All diagrams and links
- Section headings"""

        self.advanced_prompt = """You are an expert technical educator adapting robotics content for ADVANCED USERS.

Your task:
- Assume strong Python/AI/robotics foundation
- Focus on optimization, performance, edge cases
- Add advanced implementation details
- Include references to research papers and advanced techniques
- Remove basic explanations
- Add production-grade code patterns

Maintain:
- Technical accuracy
- Original markdown structure
- Code blocks (enhanced with advanced patterns)
- All diagrams and links
- Section headings"""

        self.hardware_aware_prompt = """
Additionally, adapt content based on hardware availability:
- If user has RTX GPU: Emphasize GPU-accelerated workflows, CUDA examples
- If user has Jetson: Include embedded deployment examples
- If user has robots: Encourage hands-on practice with real hardware
- If no hardware: Focus on simulation-based alternatives, cloud options
"""

    async def personalize_content(
        self,
        content: str,
        skill_level: SkillLevel,
        has_rtx_gpu: bool = False,
        has_jetson: bool = False,
        has_robots: bool = False
    ) -> Tuple[str, int]:
        """
        Personalize chapter content based on user profile.

        Args:
            content: Original markdown chapter content
            skill_level: User's skill level enum
            has_rtx_gpu: User has RTX GPU
            has_jetson: User has Jetson device
            has_robots: User has physical robots

        Returns:
            Tuple of (personalized_content, response_time_ms)
        """
        start_time = time.time()

        # Select prompt template based on skill level
        if skill_level == SkillLevel.BEGINNER:
            system_prompt = self.beginner_prompt
        elif skill_level == SkillLevel.ADVANCED:
            system_prompt = self.advanced_prompt
        else:
            # Intermediate - minimal adaptation
            system_prompt = """Adapt this robotics content for intermediate users with basic Python/AI knowledge.

Maintain technical depth while ensuring clarity. Add brief explanations for advanced concepts.
Keep all code, diagrams, and structure intact."""

        # Add hardware-aware instructions
        hardware_info = []
        if has_rtx_gpu:
            hardware_info.append("User has RTX GPU - emphasize GPU-accelerated workflows")
        if has_jetson:
            hardware_info.append("User has Jetson - include embedded deployment examples")
        if has_robots:
            hardware_info.append("User has robots - encourage hands-on practice")
        else:
            hardware_info.append("User has no physical robots - focus on simulation")

        if hardware_info:
            system_prompt += self.hardware_aware_prompt + "\n\nUser Hardware: " + ", ".join(hardware_info)

        # Build prompt
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=f"""Adapt the following chapter content:

{content}

Provide the adapted content in markdown format, preserving all structure.""")
        ]

        # Generate personalized content
        response = await self.llm.ainvoke(messages)
        personalized_content = response.content

        response_time_ms = int((time.time() - start_time) * 1000)

        return personalized_content, response_time_ms


# Global instance
personalization_service = PersonalizationService()
