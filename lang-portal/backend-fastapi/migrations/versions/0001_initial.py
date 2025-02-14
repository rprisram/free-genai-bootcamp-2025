"""Initial migration

Revision ID: 0001_initial
Revises: 
Create Date: 2024-02-20
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '0001_initial'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    # Create words table
    op.create_table(
        'words',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('japanese', sa.String, nullable=False),
        sa.Column('romaji', sa.String, nullable=False),
        sa.Column('english', sa.String, nullable=False)
    )
    
    # Create groups table
    op.create_table(
        'groups',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('name', sa.String, nullable=False)
    )
    
    # Create words_groups table
    op.create_table(
        'words_groups',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('word_id', sa.Integer, sa.ForeignKey('words.id'), nullable=False),
        sa.Column('group_id', sa.Integer, sa.ForeignKey('groups.id'), nullable=False)
    )
    
    # Create study_activities table
    op.create_table(
        'study_activities',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('name', sa.String, nullable=False),
        sa.Column('thumbnail_url', sa.String),
        sa.Column('description', sa.String)
    )
    
    # Create study_sessions table
    op.create_table(
        'study_sessions',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('group_id', sa.Integer, sa.ForeignKey('groups.id'), nullable=False),
        sa.Column('study_activity_id', sa.Integer, sa.ForeignKey('study_activities.id'), nullable=False),
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.func.now())
    )
    
    # Create word_review_items table
    op.create_table(
        'word_review_items',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('word_id', sa.Integer, sa.ForeignKey('words.id'), nullable=False),
        sa.Column('study_session_id', sa.Integer, sa.ForeignKey('study_sessions.id'), nullable=False),
        sa.Column('correct', sa.Boolean, nullable=False),
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.func.now())
    )

def downgrade():
    op.drop_table('word_review_items')
    op.drop_table('study_sessions')
    op.drop_table('study_activities')
    op.drop_table('words_groups')
    op.drop_table('groups')
    op.drop_table('words') 