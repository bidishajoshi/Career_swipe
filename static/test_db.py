import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

def test_connection():
    db_url = os.getenv("DATABASE_URL")
    
    if not db_url:
        print("ERROR: DATABASE_URL not found in .env file.")
        print("Please check your .env file and ensure DATABASE_URL is set.")
        return

    # Handle the postgres:// fix if it's there
    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)

    # Safety: Hide credentials when printing info
    display_url = db_url.split("@")[-1] if "@" in db_url else db_url
    print(f"Attempting to connect to: {display_url}")

    try:
        # For Cloud PostgreSQL (Supabase), we often need sslmode=require
        connect_args = {}
        if not db_url.startswith("sqlite"):
            connect_args = {"sslmode": "require"}

        engine = create_engine(db_url, connect_args=connect_args)
        
        # Try a simple query
        with engine.connect() as connection:
            result = connection.execute(text("SELECT version();"))
            row = result.fetchone()
            print("\nSUCCESS! Connected to the database.")
            print(f"Database Version: {row[0]}")
            
    except Exception as e:
        print("CONNECTION FAILED!")
        print(f"Error Details: {e}")
        print("\nTIPS:")
        print("1. Check if you replaced [YOUR-PASSWORD] with your actual password.")
        print("2. Ensure your database project is active and not paused.")
        print("3. Check for special characters in your password (like '@' or ':') which might need encoding.")

if __name__ == "__main__":
    test_connection()
