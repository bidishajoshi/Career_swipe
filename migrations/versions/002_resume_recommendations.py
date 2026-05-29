"""add resume recommendation tables

Revision ID: 002_resume_recommendations
Revises: add_country_eligibility
Create Date: 2026-05-28 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


revision = '002_resume_recommendations'
down_revision = 'add_country_eligibility'
branch_labels = None
depends_on = None


def _table_exists(conn, name):
    inspector = inspect(conn)
    return name in inspector.get_table_names()


def upgrade():
    conn = op.get_bind()
    if not _table_exists(conn, 'uploaded_resumes'):
        op.create_table(
            'uploaded_resumes',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('seeker_id', sa.Integer(), nullable=False),
            sa.Column('filename', sa.String(length=255), nullable=False),
            sa.Column('file_path', sa.String(length=500), nullable=False),
            sa.Column('extracted_text', sa.Text(), nullable=True),
            sa.Column('extracted_skills', sa.Text(), nullable=True),
            sa.Column('is_active', sa.Boolean(), nullable=True),
            sa.Column('created_at', sa.DateTime(), nullable=True),
            sa.Column('updated_at', sa.DateTime(), nullable=True),
            sa.ForeignKeyConstraint(['seeker_id'], ['seekers.id'], ondelete='CASCADE'),
            sa.PrimaryKeyConstraint('id')
        )
        op.create_index(op.f('ix_uploaded_resumes_is_active'), 'uploaded_resumes', ['is_active'], unique=False)
        op.create_index(op.f('ix_uploaded_resumes_seeker_id'), 'uploaded_resumes', ['seeker_id'], unique=False)

    if not _table_exists(conn, 'recommendation_history'):
        op.create_table(
            'recommendation_history',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('seeker_id', sa.Integer(), nullable=False),
            sa.Column('job_id', sa.Integer(), nullable=False),
            sa.Column('resume_id', sa.Integer(), nullable=True),
            sa.Column('similarity_score', sa.Float(), nullable=True),
            sa.Column('match_percentage', sa.Integer(), nullable=True),
            sa.Column('matched_skills', sa.Text(), nullable=True),
            sa.Column('missing_skills', sa.Text(), nullable=True),
            sa.Column('recommended_skills', sa.Text(), nullable=True),
            sa.Column('created_at', sa.DateTime(), nullable=True),
            sa.ForeignKeyConstraint(['job_id'], ['jobs.id'], ondelete='CASCADE'),
            sa.ForeignKeyConstraint(['resume_id'], ['uploaded_resumes.id'], ondelete='SET NULL'),
            sa.ForeignKeyConstraint(['seeker_id'], ['seekers.id'], ondelete='CASCADE'),
            sa.PrimaryKeyConstraint('id')
        )
        op.create_index(op.f('ix_recommendation_history_created_at'), 'recommendation_history', ['created_at'], unique=False)
        op.create_index(op.f('ix_recommendation_history_job_id'), 'recommendation_history', ['job_id'], unique=False)
        op.create_index(op.f('ix_recommendation_history_resume_id'), 'recommendation_history', ['resume_id'], unique=False)
        op.create_index(op.f('ix_recommendation_history_seeker_id'), 'recommendation_history', ['seeker_id'], unique=False)

    if not _table_exists(conn, 'saved_jobs'):
        op.create_table(
            'saved_jobs',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('seeker_id', sa.Integer(), nullable=False),
            sa.Column('job_id', sa.Integer(), nullable=False),
            sa.Column('created_at', sa.DateTime(), nullable=True),
            sa.ForeignKeyConstraint(['job_id'], ['jobs.id'], ondelete='CASCADE'),
            sa.ForeignKeyConstraint(['seeker_id'], ['seekers.id'], ondelete='CASCADE'),
            sa.PrimaryKeyConstraint('id'),
            sa.UniqueConstraint('seeker_id', 'job_id', name='uq_saved_job')
        )
        op.create_index(op.f('ix_saved_jobs_created_at'), 'saved_jobs', ['created_at'], unique=False)
        op.create_index(op.f('ix_saved_jobs_job_id'), 'saved_jobs', ['job_id'], unique=False)
        op.create_index(op.f('ix_saved_jobs_seeker_id'), 'saved_jobs', ['seeker_id'], unique=False)

    if not _table_exists(conn, 'recently_viewed_jobs'):
        op.create_table(
            'recently_viewed_jobs',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('seeker_id', sa.Integer(), nullable=False),
            sa.Column('job_id', sa.Integer(), nullable=False),
            sa.Column('viewed_at', sa.DateTime(), nullable=True),
            sa.ForeignKeyConstraint(['job_id'], ['jobs.id'], ondelete='CASCADE'),
            sa.ForeignKeyConstraint(['seeker_id'], ['seekers.id'], ondelete='CASCADE'),
            sa.PrimaryKeyConstraint('id'),
            sa.UniqueConstraint('seeker_id', 'job_id', name='uq_recently_viewed_job')
        )
        op.create_index(op.f('ix_recently_viewed_jobs_job_id'), 'recently_viewed_jobs', ['job_id'], unique=False)
        op.create_index(op.f('ix_recently_viewed_jobs_seeker_id'), 'recently_viewed_jobs', ['seeker_id'], unique=False)
        op.create_index(op.f('ix_recently_viewed_jobs_viewed_at'), 'recently_viewed_jobs', ['viewed_at'], unique=False)


def downgrade():
    op.drop_index(op.f('ix_recently_viewed_jobs_viewed_at'), table_name='recently_viewed_jobs')
    op.drop_index(op.f('ix_recently_viewed_jobs_seeker_id'), table_name='recently_viewed_jobs')
    op.drop_index(op.f('ix_recently_viewed_jobs_job_id'), table_name='recently_viewed_jobs')
    op.drop_table('recently_viewed_jobs')
    op.drop_index(op.f('ix_saved_jobs_seeker_id'), table_name='saved_jobs')
    op.drop_index(op.f('ix_saved_jobs_job_id'), table_name='saved_jobs')
    op.drop_index(op.f('ix_saved_jobs_created_at'), table_name='saved_jobs')
    op.drop_table('saved_jobs')
    op.drop_index(op.f('ix_recommendation_history_seeker_id'), table_name='recommendation_history')
    op.drop_index(op.f('ix_recommendation_history_resume_id'), table_name='recommendation_history')
    op.drop_index(op.f('ix_recommendation_history_job_id'), table_name='recommendation_history')
    op.drop_index(op.f('ix_recommendation_history_created_at'), table_name='recommendation_history')
    op.drop_table('recommendation_history')
    op.drop_index(op.f('ix_uploaded_resumes_seeker_id'), table_name='uploaded_resumes')
    op.drop_index(op.f('ix_uploaded_resumes_is_active'), table_name='uploaded_resumes')
    op.drop_table('uploaded_resumes')
