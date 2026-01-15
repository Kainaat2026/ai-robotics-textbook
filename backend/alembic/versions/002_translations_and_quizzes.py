"""Add translations and quiz system tables

Revision ID: 002
Revises: 001
Create Date: 2026-01-09

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create translations and quiz tables."""

    # Translations table
    op.create_table(
        'translations',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('content_hash', sa.String(64), nullable=False),
        sa.Column('source_language', sa.String(5), nullable=False, server_default='en'),
        sa.Column('target_language', sa.String(5), nullable=False),
        sa.Column('source_content', sa.Text(), nullable=False),
        sa.Column('translated_content', sa.Text(), nullable=False),
        sa.Column('content_type', sa.String(50), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
    )
    op.create_index('ix_translations_content_hash', 'translations', ['content_hash'])
    op.create_index('idx_translation_lookup', 'translations', ['content_hash', 'source_language', 'target_language'])

    # Create enums for quiz system
    op.execute("CREATE TYPE questiontype AS ENUM ('multiple_choice', 'true_false', 'code_completion')")
    op.execute("CREATE TYPE difficulty AS ENUM ('beginner', 'intermediate', 'advanced')")

    # Quizzes table
    op.create_table(
        'quizzes',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('chapter_id', sa.String(100), nullable=False, unique=True),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('instructions', sa.String(1000), nullable=True),
        sa.Column('passing_score', sa.Float(), nullable=False, server_default='70.0'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
    )
    op.create_index('ix_quizzes_chapter_id', 'quizzes', ['chapter_id'])

    # Quiz questions table
    op.create_table(
        'quiz_questions',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('quiz_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('order_index', sa.Integer(), nullable=False),
        sa.Column('question_text', sa.String(1000), nullable=False),
        sa.Column('question_type', sa.Enum('multiple_choice', 'true_false', 'code_completion', name='questiontype'), nullable=False),
        sa.Column('options', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('correct_answer', sa.String(500), nullable=False),
        sa.Column('explanation', sa.String(2000), nullable=True),
        sa.Column('difficulty', sa.Enum('beginner', 'intermediate', 'advanced', name='difficulty'), nullable=False, server_default='intermediate'),
        sa.Column('points', sa.Integer(), nullable=False, server_default='1'),
        sa.ForeignKeyConstraint(['quiz_id'], ['quizzes.id'], ondelete='CASCADE'),
    )

    # Quiz attempts table
    op.create_table(
        'quiz_attempts',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('quiz_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('score', sa.Float(), nullable=True),
        sa.Column('points_earned', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('total_points', sa.Integer(), nullable=False),
        sa.Column('passed', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['quiz_id'], ['quizzes.id'], ondelete='CASCADE'),
    )

    # Quiz responses table
    op.create_table(
        'quiz_responses',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('attempt_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('question_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_answer', sa.String(500), nullable=False),
        sa.Column('is_correct', sa.Boolean(), nullable=False),
        sa.Column('points_awarded', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('answered_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['attempt_id'], ['quiz_attempts.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['question_id'], ['quiz_questions.id'], ondelete='CASCADE'),
    )


def downgrade() -> None:
    """Drop translations and quiz tables."""

    # Drop tables in reverse order (respecting foreign keys)
    op.drop_table('quiz_responses')
    op.drop_table('quiz_attempts')
    op.drop_table('quiz_questions')
    op.drop_table('quizzes')
    op.drop_table('translations')

    # Drop enums
    op.execute('DROP TYPE IF EXISTS questiontype')
    op.execute('DROP TYPE IF EXISTS difficulty')
