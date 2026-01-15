"""Test quiz generation with Gemini."""
import asyncio
from src.services.quiz_service import quiz_service
from src.models.quiz import Difficulty

async def test_quiz_generation():
    """Test generating quiz for a chapter."""

    chapter_content = """
# ROS 2 Topics and Message Types

## Introduction
ROS 2 Topics enable asynchronous communication between nodes using a publish-subscribe pattern.
In this pattern, publishers send messages to topics without knowing who will receive them, and
subscribers receive messages without knowing who sent them.

## Key Concepts
- Decoupling: Publishers and subscribers are independent
- Many-to-many: Multiple publishers and subscribers per topic
- Asynchronous: Non-blocking communication
- Typed: Each topic has a specific message type
    """

    chapter_title = "ROS 2 Topics and Message Types"
    learning_objectives = [
        "Understand publish-subscribe pattern",
        "Create publishers and subscribers in Python",
        "Visualize topic communication with rqt_graph"
    ]

    print("Generating quiz questions...")
    questions = await quiz_service.generate_quiz(
        chapter_content=chapter_content,
        chapter_title=chapter_title,
        learning_objectives=learning_objectives,
        num_questions=5,
        difficulty=Difficulty.INTERMEDIATE
    )

    if questions:
        print(f"\n✅ Successfully generated {len(questions)} questions!\n")
        for i, q in enumerate(questions, 1):
            print(f"{i}. {q.get('question_text', 'N/A')}")
            print(f"   Type: {q.get('question_type', 'N/A')}")
            print(f"   Difficulty: {q.get('difficulty', 'N/A')}")
            print()
    else:
        print("❌ Failed to generate questions")

if __name__ == "__main__":
    asyncio.run(test_quiz_generation())
