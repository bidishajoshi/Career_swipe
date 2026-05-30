"""Add profile wizard fields for seekers and companies

Revision ID: add_profile_wizard_fields
Revises: add_job_positions_field
Create Date: 2026-05-30
"""
from alembic import op
import sqlalchemy as sa


revision = 'add_profile_wizard_fields'
down_revision = 'add_job_positions_field'
branch_labels = None
depends_on = None


def upgrade():
    # Seeker columns
    seeker_cols = [
        ('linkedin', sa.String(500)),
        ('portfolio', sa.String(500)),
        ('profile_photo_path', sa.String(500)),
        ('education_history', sa.Text()),
        ('certifications', sa.Text()),
        ('employment_type', sa.String(50)),
        ('source', sa.String(100)),
        ('profile_completion', sa.Integer()),
        ('draft_data', sa.Text()),
        ('is_published', sa.Boolean()),
    ]
    for name, col_type in seeker_cols:
        try:
            op.add_column('seekers', sa.Column(name, col_type, nullable=True))
        except Exception:
            pass

# Company columns addition removed per user request (seeker fields only)



def downgrade():
    seeker_drop = [
        'linkedin', 'portfolio', 'profile_photo_path', 'education_history',
        'certifications', 'employment_type', 'source', 'profile_completion',
        'draft_data', 'is_published',
    ]
    for name in seeker_drop:
        try:
            op.drop_column('seekers', name)
        except Exception:
            pass

# Company column deletions removed per user request (seeker fields only)

