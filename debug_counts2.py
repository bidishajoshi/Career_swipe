# debug_counts2.py
"""Utility script to count rows in each table of the local SQLite database career_swipe.db.
Helps verify that the SQLite file contains data before migration.
"""
import os, sys, sqlite3

# Absolute path to the SQLite DB (project root)
DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "career_swipe.db"))
if not os.path.exists(DB_PATH):
    sys.stderr.write(f"[ERROR] SQLite file not found at {DB_PATH}\n")
    sys.exit(1)

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()
cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [row[0] for row in cur.fetchall()]
print("SQLite tables:", tables)
for t in tables:
    try:
        cur.execute(f"SELECT COUNT(*) FROM {t}")
        count = cur.fetchone()[0]
        print(f"Table {t}: {count} rows")
    except Exception as e:
        print(f"Error counting {t}: {e}")
conn.close()
