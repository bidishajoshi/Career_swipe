import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

def check():
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        print("Error: DATABASE_URL not found.")
        return

    # Render fix
    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)

    print(f"Checking database at: {db_url.split('@')[-1]}")
    
    try:
        engine = create_engine(db_url, connect_args={"sslmode": "require"})
        with engine.connect() as conn:
            for table in ['companies', 'job_listings', 'seekers']:
                try:
                    result = conn.execute(text(f"SELECT count(*) FROM {table}"))
                    count = result.fetchone()[0]
                    print(f"Table '{table}': {count} rows")
                    
                    if count > 0:
                        print(f"  Sample from {table}:")
                        # Pick a column name likely to exist across most tables or handle errors
                        sample = conn.execute(text(f"SELECT * FROM {table} LIMIT 1")).fetchone()
                        print(f"  - {sample}")
                except Exception as table_err:
                    print(f"Table '{table}' might not exist yet: {table_err}")
    except Exception as e:
        print(f"Connection failed: {e}")

if __name__ == "__main__":
    check()
