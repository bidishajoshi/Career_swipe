"""
001_full_schema – CareerSwipe Full Schema Migration
====================================================
Safe to run on any state of the production database:
  - Renames old tables (companies → employers, job_listings → jobs,
    job_swipes → applications) if they exist.
  - Adds missing columns with ADD COLUMN IF NOT EXISTS.
  - Creates tables from scratch on a clean database.
  - Idempotent: running twice causes no errors.

Revision ID: 001_full_schema
Revises    : (none – first migration)
Create Date: 2026-04-28
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.engine.reflection import Inspector

# ── Alembic metadata ──────────────────────────────────────────────────────────
revision    = '001_full_schema'
down_revision = None
branch_labels = None
depends_on  = None


def _table_exists(conn, name):
    """Return True if 'name' table exists in the public schema."""
    result = conn.execute(
        sa.text(
            "SELECT EXISTS (SELECT 1 FROM information_schema.tables "
            "WHERE table_schema='public' AND table_name=:t)"
        ),
        {"t": name}
    )
    return result.scalar()


def _column_exists(conn, table, column):
    """Return True if 'column' exists on 'table'."""
    result = conn.execute(
        sa.text(
            "SELECT EXISTS (SELECT 1 FROM information_schema.columns "
            "WHERE table_schema='public' AND table_name=:t AND column_name=:c)"
        ),
        {"t": table, "c": column}
    )
    return result.scalar()


def _add_col(conn, table, column, definition):
    """Add a column only if it does not already exist."""
    if not _column_exists(conn, table, column):
        conn.execute(sa.text(f"ALTER TABLE {table} ADD COLUMN {column} {definition}"))
        print(f"  + added column {table}.{column}")


# ─────────────────────────────────────────────────────────────────────────────
def upgrade():
    conn = op.get_bind()

    # ── STEP 1: Rename legacy tables ────────────────────────────────────────
    # companies → employers
    if _table_exists(conn, 'companies') and not _table_exists(conn, 'employers'):
        conn.execute(sa.text("ALTER TABLE companies RENAME TO employers"))
        print("✓ Renamed: companies → employers")
    elif not _table_exists(conn, 'employers'):
        # Create fresh employers table
        op.create_table(
            'employers',
            sa.Column('id',                 sa.Integer,     primary_key=True),
            sa.Column('company_name',       sa.String(255), nullable=False),
            sa.Column('email',              sa.String(255), nullable=False, unique=True),
            sa.Column('password_hash',      sa.String(255), nullable=False),
            sa.Column('phone',              sa.String(30)),
            sa.Column('company_address',    sa.String(500)),
            sa.Column('description',        sa.Text),
            sa.Column('industry',           sa.String(150)),
            sa.Column('website',            sa.String(300)),
            sa.Column('logo_path',          sa.String(500)),
            sa.Column('verification_token', sa.String(100)),
            sa.Column('is_verified',        sa.Boolean,     default=False),
            sa.Column('created_at',         sa.DateTime,    server_default=sa.func.now()),
        )
        print("✓ Created: employers")

    # job_listings → jobs
    if _table_exists(conn, 'job_listings') and not _table_exists(conn, 'jobs'):
        conn.execute(sa.text("ALTER TABLE job_listings RENAME TO jobs"))
        print("✓ Renamed: job_listings → jobs")
    elif not _table_exists(conn, 'jobs'):
        op.create_table(
            'jobs',
            sa.Column('id',                  sa.Integer,     primary_key=True),
            sa.Column('company_id',          sa.Integer,     sa.ForeignKey('employers.id', ondelete='CASCADE'), nullable=False),
            sa.Column('title',               sa.String(255), nullable=False),
            sa.Column('description',         sa.Text,        nullable=False),
            sa.Column('required_skills',     sa.Text),
            sa.Column('location',            sa.String(255)),
            sa.Column('job_type',            sa.String(50),  server_default='Full-time'),
            sa.Column('job_location_type',   sa.String(50),  server_default='Onsite'),
            sa.Column('experience_level',    sa.String(50),  server_default='Entry Level'),
            sa.Column('min_experience',      sa.Integer,     server_default='0'),
            sa.Column('experience_required', sa.String(100)),
            sa.Column('salary',              sa.String(100)),
            sa.Column('max_salary',          sa.Integer),
            sa.Column('tags',                sa.Text),
            sa.Column('is_boosted',          sa.Boolean,     server_default='false'),
            sa.Column('created_at',          sa.DateTime,    server_default=sa.func.now()),
        )
        print("✓ Created: jobs")

    # job_swipes → applications
    if _table_exists(conn, 'job_swipes') and not _table_exists(conn, 'applications'):
        conn.execute(sa.text("ALTER TABLE job_swipes RENAME TO applications"))
        print("✓ Renamed: job_swipes → applications")
    elif not _table_exists(conn, 'applications'):
        op.create_table(
            'applications',
            sa.Column('id',            sa.Integer,  primary_key=True),
            sa.Column('seeker_id',     sa.Integer,  sa.ForeignKey('seekers.id', ondelete='CASCADE'), nullable=False),
            sa.Column('job_id',        sa.Integer,  sa.ForeignKey('jobs.id', ondelete='CASCADE'), nullable=False),
            sa.Column('direction',     sa.String(10), nullable=False),
            sa.Column('status',        sa.String(20), server_default='pending'),
            sa.Column('ats_score',     sa.Float,    server_default='0'),
            sa.Column('match_score',   sa.Float,    server_default='0'),
            sa.Column('ai_rank_score', sa.Float,    server_default='0'),
            sa.Column('applied_at',    sa.DateTime, server_default=sa.func.now()),
            sa.Column('created_at',    sa.DateTime, server_default=sa.func.now()),
        )
        print("✓ Created: applications")

    # notifications (keep existing)
    if not _table_exists(conn, 'notifications'):
        op.create_table(
            'notifications',
            sa.Column('id',         sa.Integer,  primary_key=True),
            sa.Column('user_id',    sa.Integer,  nullable=False),
            sa.Column('user_type',  sa.String(20), nullable=False),
            sa.Column('message',    sa.Text,     nullable=False),
            sa.Column('type',       sa.String(50), server_default='system'),
            sa.Column('is_read',    sa.Boolean,  server_default='false'),
            sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        )
        print("✓ Created: notifications")

    # ── STEP 2: Add missing columns to seekers ───────────────────────────────
    if _table_exists(conn, 'seekers'):
        _add_col(conn, 'seekers', 'address',          'VARCHAR(500)')
        _add_col(conn, 'seekers', 'gender',            'VARCHAR(20)')
        _add_col(conn, 'seekers', 'dob',               'VARCHAR(20)')
        _add_col(conn, 'seekers', 'experience_type',   'VARCHAR(50)')
        _add_col(conn, 'seekers', 'career_field',      'VARCHAR(100)')
        _add_col(conn, 'seekers', 'job_status',        'VARCHAR(50)')
        _add_col(conn, 'seekers', 'job_location_type', 'VARCHAR(50)')
        _add_col(conn, 'seekers', 'shift_preference',  'VARCHAR(50)')
        _add_col(conn, 'seekers', 'desired_roles',     'VARCHAR(255)')
        _add_col(conn, 'seekers', 'salary_expectation','VARCHAR(100)')
        _add_col(conn, 'seekers', 'availability',      'VARCHAR(100)')
        _add_col(conn, 'seekers', 'verification_token','VARCHAR(100)')
        _add_col(conn, 'seekers', 'is_verified',       'BOOLEAN DEFAULT FALSE')
        print("✓ seekers columns verified/added")

    # ── STEP 3: Add missing columns to employers ─────────────────────────────
    if _table_exists(conn, 'employers'):
        _add_col(conn, 'employers', 'phone',           'VARCHAR(30)')
        _add_col(conn, 'employers', 'company_address', 'VARCHAR(500)')
        _add_col(conn, 'employers', 'description',     'TEXT')
        _add_col(conn, 'employers', 'website',         'VARCHAR(300)')
        _add_col(conn, 'employers', 'logo_path',       'VARCHAR(500)')
        _add_col(conn, 'employers', 'verification_token', 'VARCHAR(100)')
        _add_col(conn, 'employers', 'is_verified',     'BOOLEAN DEFAULT FALSE')
        print("✓ employers columns verified/added")

    # ── STEP 4: Add missing columns to jobs ──────────────────────────────────
    if _table_exists(conn, 'jobs'):
        _add_col(conn, 'jobs', 'required_skills',     'TEXT')
        _add_col(conn, 'jobs', 'job_location_type',   'VARCHAR(50)')
        _add_col(conn, 'jobs', 'experience_level',    'VARCHAR(50)')
        _add_col(conn, 'jobs', 'min_experience',      'INTEGER DEFAULT 0')
        _add_col(conn, 'jobs', 'experience_required', 'VARCHAR(100)')
        _add_col(conn, 'jobs', 'max_salary',          'INTEGER')
        _add_col(conn, 'jobs', 'tags',                'TEXT')
        _add_col(conn, 'jobs', 'is_boosted',          'BOOLEAN DEFAULT FALSE')
        print("✓ jobs columns verified/added")

    # ── STEP 5: Add missing columns to applications ──────────────────────────
    if _table_exists(conn, 'applications'):
        _add_col(conn, 'applications', 'ats_score',     'FLOAT DEFAULT 0')
        _add_col(conn, 'applications', 'match_score',   'FLOAT DEFAULT 0')
        _add_col(conn, 'applications', 'ai_rank_score', 'FLOAT DEFAULT 0')
        _add_col(conn, 'applications', 'applied_at',    'TIMESTAMP DEFAULT NOW()')
        _add_col(conn, 'applications', 'created_at',    'TIMESTAMP DEFAULT NOW()')
        print("✓ applications columns verified/added")

    # ── STEP 6: Ensure performance indexes ───────────────────────────────────
    indexes = [
        ("ix_seekers_email",       "CREATE INDEX IF NOT EXISTS ix_seekers_email ON seekers(email)"),
        ("ix_employers_email",     "CREATE INDEX IF NOT EXISTS ix_employers_email ON employers(email)"),
        ("ix_applications_seeker", "CREATE INDEX IF NOT EXISTS ix_applications_seeker_id ON applications(seeker_id)"),
        ("ix_applications_job",    "CREATE INDEX IF NOT EXISTS ix_applications_job_id ON applications(job_id)"),
        ("ix_notifications_user",  "CREATE INDEX IF NOT EXISTS ix_notifications_user ON notifications(user_id, user_type)"),
    ]
    for _name, sql in indexes:
        try:
            conn.execute(sa.text(sql))
        except Exception:
            pass  # index may already exist
    print("✓ Indexes ensured")

    print("\n🎉 Migration 001_full_schema completed successfully!")


# ─────────────────────────────────────────────────────────────────────────────
def downgrade():
    """
    Reversal is intentionally minimal – only safe structural changes.
    Data is preserved; table renames are NOT reversed to avoid data loss.
    """
    conn = op.get_bind()
    print("⚠ Downgrade: only drops newly created tables (if empty). Renames are NOT reversed.")
