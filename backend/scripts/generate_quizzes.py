"""
Quiz Generation Script.

Batch generates quizzes for all chapters.

Usage:
    python scripts/generate_quizzes.py --docs-dir ../frontend/docs --all
    python scripts/generate_quizzes.py --chapter chapter-03-ros2-topics
"""

import asyncio
import argparse
import sys
from pathlib import Path
import frontmatter

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.db.connection import get_async_session
from src.models.quiz import Quiz, QuizQuestion, QuestionType, Difficulty
from src.services.quiz_service import quiz_service


class QuizGenerator:
    """Handles quiz generation workflow."""

    def __init__(self, docs_dir: str):
        """
        Initialize generator.

        Args:
            docs_dir: Path to docs directory
        """
        self.docs_dir = Path(docs_dir)
        if not self.docs_dir.exists():
            raise ValueError(f"Docs directory not found: {docs_dir}")

    def find_chapters(self) -> list[Path]:
        """Find all chapter markdown files."""
        chapters = []
        for module_dir in self.docs_dir.glob("module-*"):
            if module_dir.is_dir():
                chapters.extend(module_dir.glob("chapter-*.md"))
        return sorted(chapters)

    def parse_chapter(self, file_path: Path) -> dict:
        """Parse chapter file and extract metadata."""
        with open(file_path, 'r', encoding='utf-8') as f:
            post = frontmatter.load(f)

        return {
            'id': post.get('id', file_path.stem),
            'title': post.get('title', ''),
            'learning_objectives': post.get('learning_objectives', []),
            'content': post.content
        }

    async def generate_quiz_for_chapter(self, file_path: Path) -> bool:
        """
        Generate and save quiz for a chapter.

        Args:
            file_path: Path to chapter file

        Returns:
            Success status
        """
        print(f"Generating quiz for: {file_path.name}")

        # Parse chapter
        chapter_data = self.parse_chapter(file_path)
        chapter_id = chapter_data['id']
        chapter_title = chapter_data['title']
        learning_objectives = chapter_data['learning_objectives']
        content = chapter_data['content']

        if not learning_objectives:
            print(f"  ⚠ Skipping: No learning objectives defined")
            return False

        # Generate questions
        print(f"  Generating questions...")
        questions_data = await quiz_service.generate_quiz(
            chapter_content=content,
            chapter_title=chapter_title,
            learning_objectives=learning_objectives,
            num_questions=8,
            difficulty=Difficulty.INTERMEDIATE
        )

        if not questions_data:
            print(f"  ✗ Failed to generate questions")
            return False

        print(f"  Generated {len(questions_data)} questions")

        # Save to database
        async for db in get_async_session():
            try:
                # Check if quiz already exists
                from sqlalchemy import select
                stmt = select(Quiz).where(Quiz.chapter_id == chapter_id)
                result = await db.execute(stmt)
                existing_quiz = result.scalar_one_or_none()

                if existing_quiz:
                    # Delete existing quiz (cascade deletes questions)
                    await db.delete(existing_quiz)
                    await db.flush()
                    print(f"  Deleted existing quiz")

                # Create new quiz
                quiz = Quiz(
                    chapter_id=chapter_id,
                    title=f"{chapter_title} Quiz",
                    instructions="Test your understanding of the chapter concepts. Good luck!",
                    passing_score=70.0
                )
                db.add(quiz)
                await db.flush()

                # Create questions
                for q_data in questions_data:
                    question = QuizQuestion(
                        quiz_id=quiz.id,
                        order_index=q_data['order_index'],
                        question_text=q_data['question_text'],
                        question_type=QuestionType(q_data['question_type']),
                        options=q_data.get('options'),
                        correct_answer=q_data['correct_answer'],
                        explanation=q_data.get('explanation'),
                        difficulty=Difficulty(q_data.get('difficulty', 'intermediate')),
                        points=q_data.get('points', 1)
                    )
                    db.add(question)

                await db.commit()
                print(f"  ✓ Saved quiz with {len(questions_data)} questions")
                return True

            except Exception as e:
                print(f"  ✗ Database error: {e}")
                await db.rollback()
                return False

    async def generate_all(self):
        """Generate quizzes for all chapters."""
        chapters = self.find_chapters()

        if not chapters:
            print("No chapter files found!")
            return

        print(f"Found {len(chapters)} chapters\n")

        successes = 0
        for chapter_file in chapters:
            try:
                success = await self.generate_quiz_for_chapter(chapter_file)
                if success:
                    successes += 1
                print()  # Blank line between chapters
            except Exception as e:
                print(f"  ✗ Error: {e}\n")

        print(f"\n=== Summary ===")
        print(f"Successfully generated: {successes}/{len(chapters)} quizzes")


async def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Generate quizzes for chapters")
    parser.add_argument('--docs-dir', default='../frontend/docs', help='Path to docs directory')
    parser.add_argument('--chapter', help='Generate quiz for specific chapter')
    parser.add_argument('--all', action='store_true', help='Generate quizzes for all chapters')

    args = parser.parse_args()

    generator = QuizGenerator(args.docs_dir)

    if args.all:
        print("=== Generating Quizzes for All Chapters ===\n")
        await generator.generate_all()

    elif args.chapter:
        # Find specific chapter
        chapters = generator.find_chapters()
        target = None
        for ch in chapters:
            if args.chapter in ch.stem:
                target = ch
                break

        if target:
            await generator.generate_quiz_for_chapter(target)
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
