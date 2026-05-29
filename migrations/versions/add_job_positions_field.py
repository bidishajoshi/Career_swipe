"""Add job positions field

Revision ID: add_job_positions_field
Revises: add_country_eligibility
Create Date: 2026-05-28 000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


# revision identifiers, used by Alembic.
revision = 'add_job_positions_field'
down_revision = '002_resume_recommendations'
branch_labels = None
depends_on = None


def _column_exists(conn, table, column):
    inspector = inspect(conn)
    return any(c['name'] == column for c in inspector.get_columns(table))


def upgrade():
    conn = op.get_bind()
    with op.batch_alter_table('jobs', schema=None) as batch_op:
        if not _column_exists(conn, 'jobs', 'number_of_positions'):
            batch_op.add_column(
                sa.Column('number_of_positions', sa.Integer(), nullable=False, server_default='1')
            )


def downgrade():
    with op.batch_alter_table('jobs', schema=None) as batch_op:
        batch_op.drop_column('number_of_positions')
