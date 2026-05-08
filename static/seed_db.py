from app import app
from extensions import db
from models import Company, JobListing, Seeker, JobSwipe
from werkzeug.security import generate_password_hash

def seed():
    with app.app_context():
        print("Clearing old data...")
        JobSwipe.query.delete()
        JobListing.query.delete()
        Seeker.query.delete()
        Company.query.delete()
        db.session.commit()

        print("Seeding database with premium fake data...")

        # Create test companies
        password = generate_password_hash("password123")
        
        google = Company(
            company_name="Google",
            email="hr@google.com",
            password_hash=password,
            description="Global technology leader focusing on search, advertising, and cloud.",
            industry="Technology",
            website="https://google.com",
            is_verified=True
        )
        
        meta = Company(
            company_name="Meta",
            email="careers@meta.com",
            password_hash=password,
            description="Giving people the power to build community and bring the world closer together.",
            industry="Social Media / AI",
            website="https://meta.com",
            is_verified=True
        )

        db.session.add(google)
        db.session.add(meta)
        db.session.commit()

        # Create job listings
        jobs = [
            JobListing(
                company_id=google.id,
                title="Senior Software Engineer (AI)",
                description="Join the team building the next generation of search experiences using Large Language Models.",
                required_skills="Python, PyTorch, SQL, Distributed Systems",
                location="Mountain View, CA",
                job_type="Full-time",
                job_location_type="Onsite",
                salary="$180,000 - $250,000",
                experience_level="Senior",
                min_experience=5,
                tags="python,ai,google"
            ),
            JobListing(
                company_id=google.id,
                title="Frontend Engineer (React)",
                description="Build high-performance UIs for our cloud management console.",
                required_skills="React, TypeScript, CSS, Testing",
                location="Zurich, Switzerland",
                job_type="Full-time",
                job_location_type="Hybrid",
                salary="140,000 CHF - 190,000 CHF",
                experience_level="Mid",
                min_experience=3,
                tags="react,frontend,cloud"
            ),
            JobListing(
                company_id=meta.id,
                title="Product Designer",
                description="Design the future of social interaction in the metaverse.",
                required_skills="Figma, UI/UX, Prototyping",
                location="Remote",
                job_type="Full-time",
                job_location_type="Remote",
                salary="$130,000 - $170,000",
                experience_level="Mid",
                min_experience=2,
                tags="design,remote,meta"
            )
        ]

        for job in jobs:
            db.session.add(job)
        
        db.session.commit()
        print("\nSUCCESS!")
        print(f"Created 2 Companies (Google, Meta)")
        print(f"Created 3 Job Listings")
        print("\n------------------------------------------------")
        print("Login Info for testing:")
        print("Email: hr@google.com")
        print("Email: careers@meta.com")
        print("Password for both: password123")
        print("------------------------------------------------")

if __name__ == "__main__":
    seed()
