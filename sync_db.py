import os
from logging_helper import logger
from sqlalchemy import create_engine, MetaData, Table, select, func
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.orm import sessionmaker
from extensions import db
from models import Company, JobListing, Seeker, UploadedResume, SavedJob, RecentlyViewedJob, RecommendationHistory, JobSwipe, Notification

# Optional: load .env file if present (requires python-dotenv)
try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

# Helper to build a full PostgreSQL URL from separate env vars (more secure than embedding password in a single var)
def build_remote_url() -> str:
    """Construct a PostgreSQL connection URL.
    Expected env vars:
      REMOTE_DB_USER, REMOTE_DB_PASSWORD, REMOTE_DB_HOST, REMOTE_DB_NAME
    If any are missing, fall back to REMOTE_DATABASE_URL or DATABASE_URL.
    The returned URL always includes sslmode=require as required by Render.
    """
    user = os.getenv('REMOTE_DB_USER')
    password = os.getenv('REMOTE_DB_PASSWORD')
    host = os.getenv('REMOTE_DB_HOST')
    name = os.getenv('REMOTE_DB_NAME')
    if all([user, password, host, name]):
        return f"postgresql://{user}:{password}@{host}/{name}?sslmode=require"
    # Fallback to pre‑built URL env vars
    url = os.getenv('REMOTE_DATABASE_URL') or os.getenv('DATABASE_URL')
    if url:
        # Ensure SSL mode is enforced
        if url.startswith('postgresql://') and 'sslmode' not in url:
            separator = '&' if '?' in url else '?'
            url = f"{url}{separator}sslmode=require"
        return url
    raise RuntimeError('No remote database connection information found. Set REMOTE_DB_* env vars or REMOTE_DATABASE_URL.')


def get_session(engine):
    """Return a new SQLAlchemy ORM session bound to the given engine."""
    Session = sessionmaker(bind=engine)
    return Session()

def is_sqlite(url: str) -> bool:
    """Return True if the given SQLAlchemy URL points to a SQLite database."""
    return url.startswith('sqlite')
def get_engine(database_url: str | None = None):
    """Create a SQLAlchemy engine based on the DATABASE_URL env var or a SQLite fallback."""
    if not database_url:
        database_url = os.getenv('DATABASE_URL')
    if not database_url:
        database_url = 'sqlite:///career_swipe.db'
    engine = create_engine(database_url, echo=False, future=True)
    # Ensure tables exist for both SQLite and PostgreSQL
    db.metadata.create_all(engine)
    return engine

def copy_table(src_engine, dst_engine, model):
    """Copy all rows from a source table to a destination table, avoiding duplicates.
    Uses PostgreSQL's INSERT ... ON CONFLICT DO NOTHING when the destination is PostgreSQL.
    """
    src_meta = MetaData()
    src_table = Table(model.__tablename__, src_meta, autoload_with=src_engine)
    dst_meta = MetaData()
    dst_table = Table(model.__tablename__, dst_meta, autoload_with=dst_engine)
    with src_engine.connect() as src_conn, dst_engine.connect() as dst_conn:
        rows = src_conn.execute(select(src_table)).fetchall()
        if not rows:
            logger.info(f"No data to copy for {model.__tablename__}")
            return
        if not is_sqlite(str(dst_engine.url)):
            stmt = pg_insert(dst_table).values([dict(row) for row in rows])
            stmt = stmt.on_conflict_do_nothing()
        else:
            stmt = dst_table.insert().values([dict(row) for row in rows])
        dst_conn.execute(stmt)
        dst_conn.commit()
        logger.info(f"Copied {len(rows)} rows to {model.__tablename__}")

def sync_databases():
    """Synchronise data from the local SQLite database to the remote PostgreSQL database (or vice‑versa depending on env)."""
    # Source is always the local SQLite database
    src_engine = get_engine('sqlite:///career_swipe.db')
    # Build destination URL securely
    # Build destination URL securely
    try:
        remote_url = build_remote_url()
    except Exception as e:
        logger.error(str(e))
        return
    # Verify remote URL includes password (required for authentication)
    from urllib.parse import urlparse
    parsed = urlparse(remote_url)
    if not parsed.password:
        logger.error('Remote URL missing password. Set REMOTE_DB_PASSWORD or include password in REMOTE_DATABASE_URL.')
        return
    # Ensure SSL mode is enforced (already handled in build_remote_url)
    # Create destination engine and handle connection errors gracefully
    try:
        dst_engine = get_engine(remote_url)
    except Exception as e:
        logger.error(f'Failed to connect to remote DB: {e}')
        return
    models = [Company, JobListing, Seeker, UploadedResume, SavedJob,
              RecentlyViewedJob, RecommendationHistory, JobSwipe, Notification]
    for model in models:
        copy_table(src_engine, dst_engine, model)
        # Verify row count and show sample rows in destination
        try:
            session = get_session(dst_engine)
            # Count rows in the destination table
            dest_table = Table(model.__tablename__, MetaData(), autoload_with=dst_engine)
            count = session.query(func.count()).select_from(dest_table)
            logger.info(f'Table `{model.__tablename__}` now has {count.scalar()} rows in destination.')
            # Show up to 5 sample rows for quick verification
            rows = session.execute(select(dest_table).limit(5)).fetchall()
            if rows:
                logger.info(f'Sample rows from `{model.__tablename__}`: {rows}')
        except Exception as exc:
            logger.warning(f'Could not fetch info for {model.__tablename__}: {exc}')
    logger.info('Database sync complete.')

if __name__ == '__main__':
    sync_databases()
