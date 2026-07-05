# migrate_sqlite_to_postgres.py
"""Utility script to migrate local SQLite data (career_swipe.db) to the PostgreSQL instance used on Render.

Features:
- Uses the same SQLAlchemy models defined in the project, guaranteeing column alignment.
- Detects the target database automatically via the ``DATABASE_URL`` environment variable.
- Copies tables in dependency order (primary‑key tables first) using ``metadata.sorted_tables``.
- Preserves primary keys, foreign keys and all timestamps.
- Skips records that already exist in the destination (based on primary‑key values).
- Runs the whole migration inside a transaction; on any error the PostgreSQL side rolls back.
- Prints progress counters for each model.

Run with:
    python migrate_sqlite_to_postgres.py
"""

import os
import sys
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker
from extensions import db as flask_db
from models import *  # Import all model classes so they are registered with the metadata

# -----------------------------------------------------------------------------
# Configuration
# -----------------------------------------------------------------------------
SQLITE_DB_PATH = os.path.abspath("career_swipe.db")
SQLITE_URL = f"sqlite:///{SQLITE_DB_PATH}"
POSTGRES_URL = os.getenv("DATABASE_URL")

if not POSTGRES_URL:
    sys.stderr.write(
        "[ERROR] DATABASE_URL environment variable not set. "
        "Provide the Postgres connection string before running the script.\n"
    )
    sys.exit(1)

# -----------------------------------------------------------------------------
# Engine / Session setup
# -----------------------------------------------------------------------------
engine_sqlite = create_engine(SQLITE_URL, future=True)
# Reflect SQLite schema into its own MetaData to avoid conflicts with Flask metadata
from sqlalchemy import MetaData
sqlite_metadata = MetaData()
sqlite_metadata.reflect(bind=engine_sqlite)
engine_pg = create_engine(POSTGRES_URL, future=True)

SessionSqlite = sessionmaker(bind=engine_sqlite, future=True)
SessionPG = sessionmaker(bind=engine_pg, future=True)

# Use Flask app metadata for destination (PostgreSQL) which includes model definitions
metadata = flask_db.metadata

def pk_dict(table, instance):
    """Return a dict of primary‑key column names and values for a SQLAlchemy instance."""
    return {col.name: getattr(instance, col.name) for col in table.primary_key.columns}

def record_exists(pg_session, table, pk):
    """Check whether a row with the given primary‑key already exists in Postgres."""
    stmt = select(table).filter_by(**pk)
    return pg_session.execute(stmt).first() is not None

def migrate_table(sqlite_session, pg_session, src_table, dest_table):
    """Migrate rows from src_table (SQLite) to dest_table (PostgreSQL)."""
    inserted = 0
    stmt = select(src_table)
    result = sqlite_session.execute(stmt)
    rows = result.fetchall()
    for row in rows:
        # Convert the RowMapping to a dictionary
        row_dict = dict(row)
        pk = {col.name: row_dict[col.name] for col in src_table.primary_key.columns}
        if record_exists(pg_session, dest_table, pk):
            continue
        pg_session.execute(dest_table.insert().values(**row_dict))
        inserted += 1
    return inserted

def main():
    print("Starting migration from SQLite to PostgreSQL")
    with SessionSqlite() as sqlite_session, SessionPG() as pg_session:
        with pg_session.begin():
            for src_table in sqlite_metadata.sorted_tables:
                dest_table = metadata.tables.get(src_table.name)
                if dest_table is None:
                    print(f"[WARN] No destination table for {src_table.name}, skipping.")
                    continue
                print(f"\nMigrating table: {src_table.name}")
                count = migrate_table(sqlite_session, pg_session, src_table, dest_table)
                print(f"   Rows inserted: {count}")
    print("\n✅ Migration completed successfully.")

if __name__ == "__main__":
    main()
