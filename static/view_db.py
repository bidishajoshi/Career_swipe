#!/usr/bin/env python3
"""Quick database viewer - Run with: python view_db.py"""
import os
from app import app, db
from models import Seeker, Company, JobListing, JobSwipe, Notification
# view_db.py
from app import create_app, db

app = create_app()

with app.app_context():
    print(db.engine.table_names())

def safe_getattr(obj, attr):
    """Safely get attribute, returns N/A if doesn't exist"""
    try:
        val = getattr(obj, attr, "N/A")
        if hasattr(val, 'strftime'):  # datetime
            val = val.strftime("%Y-%m-%d %H:%M")
        return str(val)[:20]
    except:
        return "N/A"

def print_table(title, items, columns):
    """Pretty print table data"""
    print(f"\n{'='*80}")
    print(f"  {title} ({len(items)} records)")
    print(f"{'='*80}")
    
    if not items:
        print("  No records found.")
        return
    
    # Print headers
    print("  " + " | ".join(f"{col:20}" for col in columns))
    print("  " + "-" * 78)
    
    # Print rows
    for item in items[:10]:  # Limit to 10 rows
        values = [safe_getattr(item, col) for col in columns]
        print("  " + " | ".join(f"{v:20}" for v in values))
    
    if len(items) > 10:
        print(f"  ... and {len(items) - 10} more")

def main():
    with app.app_context():
        try:
            seekers = Seeker.query.all()
            print_table("SEEKERS", seekers, ["id", "first_name", "email", "skills", "created_at"])
        except Exception as e:
            print(f"\n❌ SEEKERS: {str(e)[:60]}...")
        
        try:
            companies = Company.query.all()
            print_table("COMPANIES", companies, ["id", "company_name", "email", "industry", "created_at"])
        except Exception as e:
            print(f"\n❌ COMPANIES: {str(e)[:60]}...")
        
        try:
            jobs = JobListing.query.all()
            print_table("JOB LISTINGS", jobs, ["id", "title", "location", "job_type", "created_at"])
        except Exception as e:
            print(f"\n❌ JOB LISTINGS: {str(e)[:60]}...")
        
        try:
            swipes = JobSwipe.query.all()
            print_table("SWIPES (Applications)", swipes, ["id", "seeker_id", "job_id", "direction", "status"])
        except Exception as e:
            print(f"\n❌ SWIPES: {str(e)[:60]}...")
        
        try:
            notifications = Notification.query.all()
            print_table("NOTIFICATIONS", notifications, ["id", "user_id", "message", "type", "is_read"])
        except Exception as e:
            print(f"\n❌ NOTIFICATIONS: {str(e)[:60]}...")
        
        print(f"\n{'='*80}\n")

if __name__ == "__main__":
    main()
