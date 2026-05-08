"""
fix_schema.py -- Directly add missing columns & fix table names in the production database.
Run with:  python fix_schema.py
"""
import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()


def table_exists(conn, name):
    return conn.execute(text(
        "SELECT EXISTS (SELECT 1 FROM information_schema.tables "
        "WHERE table_schema='public' AND table_name=:t)"
    ), {"t": name}).scalar()


def col_exists(conn, table, col):
    return conn.execute(text(
        "SELECT EXISTS (SELECT 1 FROM information_schema.columns "
        "WHERE table_schema='public' AND table_name=:t AND column_name=:c)"
    ), {"t": table, "c": col}).scalar()


def add_col(conn, table, col, defn):
    if not col_exists(conn, table, col):
        conn.execute(text(f"ALTER TABLE {table} ADD COLUMN {col} {defn}"))
        print(f"  [+] Added: {table}.{col}")
    else:
        print(f"  [=] OK:    {table}.{col}")


def fix():
    db_url = os.getenv("DATABASE_URL", "")
    if not db_url:
        print("ERROR: DATABASE_URL not set in .env")
        return

    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)

    print(f"[INFO] Connecting to: {db_url.split('@')[-1]}")

    engine = create_engine(db_url, connect_args={"sslmode": "require"})

    with engine.begin() as conn:

        # ── STEP 1: Rename legacy tables if needed ───────────────────────────
        print("\n[STEP 1] Checking table names...")

        if table_exists(conn, 'companies') and not table_exists(conn, 'employers'):
            conn.execute(text("ALTER TABLE companies RENAME TO employers"))
            print("  [+] Renamed: companies -> employers")
        elif table_exists(conn, 'employers'):
            print("  [=] OK: employers table exists")
        else:
            print("  [!] Neither companies nor employers table found - will need full migration")

        if table_exists(conn, 'job_listings') and not table_exists(conn, 'jobs'):
            conn.execute(text("ALTER TABLE job_listings RENAME TO jobs"))
            print("  [+] Renamed: job_listings -> jobs")
        elif table_exists(conn, 'jobs'):
            print("  [=] OK: jobs table exists")
        else:
            print("  [!] Neither job_listings nor jobs table found")

        if table_exists(conn, 'job_swipes') and not table_exists(conn, 'applications'):
            conn.execute(text("ALTER TABLE job_swipes RENAME TO applications"))
            print("  [+] Renamed: job_swipes -> applications")
        elif table_exists(conn, 'applications'):
            print("  [=] OK: applications table exists")
        else:
            print("  [!] Neither job_swipes nor applications table found")

        # ── STEP 2: seekers columns ──────────────────────────────────────────
        print("\n[STEP 2] seekers table columns...")
        if table_exists(conn, 'seekers'):
            seekers_cols = [
                ("address",           "VARCHAR(500)"),
                ("gender",            "VARCHAR(20)"),
                ("dob",               "VARCHAR(20)"),
                ("experience_type",   "VARCHAR(50)"),
                ("career_field",      "VARCHAR(100)"),
                ("job_status",        "VARCHAR(50)"),
                ("job_location_type", "VARCHAR(50)"),
                ("shift_preference",  "VARCHAR(50)"),
                ("desired_roles",     "VARCHAR(255)"),
                ("salary_expectation","VARCHAR(100)"),
                ("availability",      "VARCHAR(100)"),
                ("verification_token","VARCHAR(100)"),
                ("is_verified",       "BOOLEAN DEFAULT FALSE"),
            ]
            for col, defn in seekers_cols:
                add_col(conn, 'seekers', col, defn)
        else:
            print("  [!] seekers table not found")

        # ── STEP 3: employers columns ────────────────────────────────────────
        print("\n[STEP 3] employers table columns...")
        if table_exists(conn, 'employers'):
            employers_cols = [
                ("phone",              "VARCHAR(30)"),
                ("company_address",    "VARCHAR(500)"),
                ("description",        "TEXT"),
                ("website",            "VARCHAR(300)"),
                ("logo_path",          "VARCHAR(500)"),
                ("verification_token", "VARCHAR(100)"),
                ("is_verified",        "BOOLEAN DEFAULT FALSE"),
            ]
            for col, defn in employers_cols:
                add_col(conn, 'employers', col, defn)
        else:
            print("  [!] employers table not found - skipping")

        # ── STEP 4: jobs columns ─────────────────────────────────────────────
        print("\n[STEP 4] jobs table columns...")
        if table_exists(conn, 'jobs'):
            jobs_cols = [
                ("required_skills",     "TEXT"),
                ("job_location_type",   "VARCHAR(50)"),
                ("experience_level",    "VARCHAR(50)"),
                ("min_experience",      "INTEGER DEFAULT 0"),
                ("experience_required", "VARCHAR(100)"),
                ("max_salary",          "INTEGER"),
                ("tags",                "TEXT"),
                ("is_boosted",          "BOOLEAN DEFAULT FALSE"),
            ]
            for col, defn in jobs_cols:
                add_col(conn, 'jobs', col, defn)
        else:
            print("  [!] jobs table not found - skipping")

        # ── STEP 5: applications columns ─────────────────────────────────────
        print("\n[STEP 5] applications table columns...")
        if table_exists(conn, 'applications'):
            apps_cols = [
                ("ats_score",     "FLOAT DEFAULT 0"),
                ("match_score",   "FLOAT DEFAULT 0"),
                ("ai_rank_score", "FLOAT DEFAULT 0"),
                ("applied_at",    "TIMESTAMP DEFAULT NOW()"),
                ("created_at",    "TIMESTAMP DEFAULT NOW()"),
            ]
            for col, defn in apps_cols:
                add_col(conn, 'applications', col, defn)
        else:
            print("  [!] applications table not found - skipping")

        # ── STEP 6: Print current table list ─────────────────────────────────
        print("\n[STEP 6] Current tables in database:")
        tables = conn.execute(text(
            "SELECT table_name FROM information_schema.tables "
            "WHERE table_schema='public' ORDER BY table_name"
        )).fetchall()
        for (t,) in tables:
            print(f"  - {t}")

        print("\n[DONE] Schema fix complete!")


if __name__ == "__main__":
    fix()
