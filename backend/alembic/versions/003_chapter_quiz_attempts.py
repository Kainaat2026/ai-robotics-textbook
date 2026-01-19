"""Add chapter_quiz_attempts table for simple progress tracking

Revision ID: 003
Revises: 002
Create Date: 2026-01-16

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '003'
down_revision = '002'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create chapter_quiz_attempts table for simple progress tracking."""

    op.create_table(
        'chapter_quiz_attempts',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('chapter_id', sa.String(100), nullable=False),
        sa.Column('score', sa.Float(), nullable=False),
        sa.Column('correct_answers', sa.Integer(), nullable=False),
        sa.Column('total_questions', sa.Integer(), nullable=False),
        sa.Column('time_taken_seconds', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    )
    op.create_index('ix_chapter_quiz_attempts_user_id', 'chapter_quiz_attempts', ['user_id'])
    op.create_index('ix_chapter_quiz_attempts_chapter_id', 'chapter_quiz_attempts', ['chapter_id'])


def downgrade() -> None:
    """Drop chapter_quiz_attempts table."""
    op.drop_index('ix_chapter_quiz_attempts_chapter_id', 'chapter_quiz_attempts')
    op.drop_index('ix_chapter_quiz_attempts_user_id', 'chapter_quiz_attempts')
    op.drop_table('chapter_quiz_attempts')
