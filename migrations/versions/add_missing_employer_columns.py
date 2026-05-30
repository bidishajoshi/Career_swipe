"""Add missing employer columns

Revision ID: add_missing_employer_columns
Revises: add_profile_wizard_fields
Create Date: 2026-05-30
"""

from alembic import op
import sqlalchemy as sa

revision = 'add_missing_employer_columns'
down_revision = 'add_profile_wizard_fields'
branch_labels = None
depends_on = None


def upgrade():
    # Columns missing in the employers table compared to models.py
    columns = [
        ('hr_name', sa.String(150)),
        ('headquarters', sa.String(255)),
        ('mission', sa.Text()),
        ('vision', sa.Text()),
        ('culture', sa.Text()),
        ('perks', sa.Text()),
        ('company_type', sa.String(100)),
        ('company_size', sa.String(50)),
        ('founded_year', sa.Integer()),
        ('banner_path', sa.String(500)),
        ('gallery_paths', sa.Text()),
        ('hiring_frequency', sa.String(50)),
        ('remote_hiring', sa.Boolean()),
        ('international_hiring', sa.Boolean()),
        ('preferred_locations', sa.Text()),
        ('hiring_categories', sa.Text()),
        ('work_mode', sa.String(50)),
        ('open_positions', sa.Text()),
        ('number_of_vacancies', sa.Integer()),
        ('linkedin_url', sa.String(500)),
        ('facebook_url', sa.String(500)),
        ('instagram_url', sa.String(500)),
        ('twitter_url', sa.String(500)),
        ('youtube_url', sa.String(500)),
        ('business_registration', sa.String(150)),
        ('verification_document', sa.String(500)),
        ('profile_completion', sa.Integer()),
        ('draft_data', sa.Text()),
        ('is_published', sa.Boolean()),
        ('notification_enabled', sa.Boolean()),
        ('last_login', sa.DateTime()),
    ]
    for name, col_type in columns:
        try:
            op.add_column('employers', sa.Column(name, col_type, nullable=True))
        except Exception:
            pass


def downgrade():
    columns = [
        'hr_name', 'headquarters', 'mission', 'vision', 'culture', 'perks',
        'company_type', 'company_size', 'founded_year', 'banner_path',
        'gallery_paths', 'hiring_frequency', 'remote_hiring', 'international_hiring',
        'preferred_locations', 'hiring_categories', 'work_mode', 'open_positions',
        'number_of_vacancies', 'linkedin_url', 'facebook_url', 'instagram_url',
        'twitter_url', 'youtube_url', 'business_registration', 'verification_document',
        'profile_completion', 'draft_data', 'is_published', 'notification_enabled',
        'last_login'
    ]
    for name in columns:
        try:
            op.drop_column('employers', name)
        except Exception:
            pass
