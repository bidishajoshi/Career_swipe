# -*- coding: utf-8 -*-
"""scripts/seed_postgres.py

Production‑ready PostgreSQL seeding script for the CareerSwipe project.
It connects to the Render PostgreSQL database via the ``DATABASE_URL``
environment variable, creates tables (SQLAlchemy models) if missing and
populates the database with realistic Nepal‑based demo data.
The script is **idempotent** – re‑running it never creates duplicate rows.

Usage:
    $ python scripts/seed_postgres.py

Make sure ``DATABASE_URL`` points to your Render PostgreSQL instance before
running the script.
"""

import os
import sys
import random
import json
import hashlib
from datetime import datetime, timedelta
from pathlib import Path

from faker import Faker
from sqlalchemy import (
    Column,
    String,
    Integer,
    Float,
    Text,
    Date,
    DateTime,
    Boolean,
    ForeignKey,
    UniqueConstraint,
    create_engine,
)
from sqlalchemy.orm import relationship, sessionmaker, declarative_base

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
fake = Faker()

# Environment variable – Render provides this automatically
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    print("[!] DATABASE_URL environment variable not set.")
    sys.exit(1)

engine = create_engine(DATABASE_URL, echo=False, future=True)
Session = sessionmaker(bind=engine, future=True)
Base = declarative_base()

# ---------------------------------------------------------------------------
# Models (only what we need for the demo). Unique constraints protect against
# duplicate inserts when the script is run multiple times.
# ---------------------------------------------------------------------------

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    email = Column(String(255), nullable=False, unique=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(50), nullable=False)  # super_admin, company_admin, job_seeker
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    company = relationship("Company", back_populates="admin", uselist=False)
    seeker_profile = relationship("JobSeeker", back_populates="user", uselist=False)

    # -----------------------------------------------------------------------
    # Password handling – using **bcrypt** for production security.
    # -----------------------------------------------------------------------
    def set_password(self, password: str):
        import bcrypt
        salt = bcrypt.gensalt()
        self.password_hash = bcrypt.hashpw(password.encode(), salt).decode()

    def check_password(self, password: str) -> bool:
        import bcrypt
        return bcrypt.checkpw(password.encode(), self.password_hash.encode())


class Company(Base):
    __tablename__ = "companies"
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False, unique=True)
    industry = Column(String(100), nullable=False)
    email = Column(String(255), nullable=False, unique=True)
    website = Column(String(255), nullable=False)
    phone = Column(String(50), nullable=False)
    description = Column(Text, nullable=False)
    address = Column(String(255), nullable=False)
    logo_url = Column(String(255), nullable=False, default="https://via.placeholder.com/150")
    hr_name = Column(String(255), nullable=False)
    hr_position = Column(String(100), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    admin_id = Column(Integer, ForeignKey("users.id"), unique=True)
    admin = relationship("User", back_populates="company")
    jobs = relationship("Job", back_populates="company", cascade="all, delete-orphan")


class JobSeeker(Base):
    __tablename__ = "job_seekers"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    full_name = Column(String(255), nullable=False)
    phone = Column(String(50), nullable=False)
    location = Column(String(100), nullable=False)
    education = Column(String(100), nullable=False)
    university = Column(String(255), nullable=False)
    graduation_year = Column(Integer, nullable=False)
    years_experience = Column(Integer, nullable=False)
    current_position = Column(String(100), nullable=False)
    expected_salary_npr = Column(Integer, nullable=False)
    resume_summary = Column(Text, nullable=False)
    linkedin_url = Column(String(255), nullable=False)
    portfolio_url = Column(String(255), nullable=True)
    profile_photo_url = Column(String(255), nullable=False, default="https://via.placeholder.com/150")
    skills_json = Column(Text, nullable=False)  # JSON list of strings
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="seeker_profile")
    applications = relationship("Application", back_populates="seeker", cascade="all, delete-orphan")
    saved_jobs = relationship("SavedJob", back_populates="seeker", cascade="all, delete-orphan")

    @property
    def skills(self):
        return json.loads(self.skills_json)


class Job(Base):
    __tablename__ = "jobs"
    id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    category = Column(String(100), nullable=False)
    employment_type = Column(String(50), nullable=False)
    experience_required = Column(String(50), nullable=False)
    education_required = Column(String(100), nullable=False)
    location = Column(String(100), nullable=False)
    salary_min_npr = Column(Integer, nullable=False)
    salary_max_npr = Column(Integer, nullable=False)
    vacancies = Column(Integer, nullable=False)
    description = Column(Text, nullable=False)
    required_skills_json = Column(Text, nullable=False)
    responsibilities = Column(Text, nullable=False)
    benefits = Column(Text, nullable=False)
    posted_date = Column(Date, nullable=False)
    deadline = Column(Date, nullable=False)
    remote_status = Column(String(20), nullable=False)  # Remote/Hybrid/On-site
    created_at = Column(DateTime, default=datetime.utcnow)

    company = relationship("Company", back_populates="jobs")
    applications = relationship("Application", back_populates="job", cascade="all, delete-orphan")
    saved_by = relationship("SavedJob", back_populates="job", cascade="all, delete-orphan")

    @property
    def required_skills(self):
        return json.loads(self.required_skills_json)


class Application(Base):
    __tablename__ = "applications"
    id = Column(Integer, primary_key=True)
    seeker_id = Column(Integer, ForeignKey("job_seekers.id"), nullable=False)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=False)
    applied_at = Column(DateTime, default=datetime.utcnow)
    status = Column(String(50), nullable=False)  # Applied, Interviewed, etc.
    notes = Column(Text, nullable=True)

    seeker = relationship("JobSeeker", back_populates="applications")
    job = relationship("Job", back_populates="applications")

    __table_args__ = (UniqueConstraint('seeker_id', 'job_id', name='_seeker_job_uc'),)


class SavedJob(Base):
    __tablename__ = "saved_jobs"
    id = Column(Integer, primary_key=True)
    seeker_id = Column(Integer, ForeignKey("job_seekers.id"), nullable=False)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=False)
    saved_at = Column(DateTime, default=datetime.utcnow)

    seeker = relationship("JobSeeker", back_populates="saved_jobs")
    job = relationship("Job", back_populates="saved_by")

    __table_args__ = (UniqueConstraint('seeker_id', 'job_id', name='_saved_seeker_job_uc'),)


class Notification(Base):
    __tablename__ = "notifications"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    read = Column(Boolean, default=False)

    user = relationship("User")

# ---------------------------------------------------------------------------
# Reference data
# ---------------------------------------------------------------------------
NEPAL_LOCATIONS = [
    "Kathmandu",
    "Lalitpur",
    "Bhaktapur",
    "Pokhara",
    "Bharatpur",
    "Biratnagar",
    "Butwal",
    "Hetauda",
    "Dharan",
    "Nepalgunj",
    "Janakpur",
    "Dhangadhi",
]

COMPANY_INDUSTRIES = [
    "IT",
    "Banking",
    "Healthcare",
    "Education",
    "Engineering",
    "Manufacturing",
    "Construction",
    "Hospitality",
    "Tourism",
    "Retail",
    "Agriculture",
    "NGOs",
    "Government",
    "Media",
    "Logistics",
]

JOB_SEEKER_CATEGORIES = [
    "Software Engineer",
    "Web Developer",
    "Data Analyst",
    "Graphic Designer",
    "UI/UX Designer",
    "Digital Marketer",
    "Accountant",
    "HR Officer",
    "Civil Engineer",
    "Mechanical Engineer",
    "Electrical Engineer",
    "Project Manager",
    "Business Analyst",
    "Sales Executive",
    "Customer Support",
    "Logistics Officer",
]

JOB_TITLES = [
    "Software Engineer",
    "QA Engineer",
    "Python Developer",
    "Frontend Developer",
    "Backend Developer",
    "Accountant",
    "Financial Analyst",
    "Bank Teller",
    "Teacher",
    "Lecturer",
    "Nurse",
    "Doctor",
    "Pharmacist",
    "Civil Engineer",
    "Mechanical Engineer",
    "HR Officer",
    "HR Manager",
    "Marketing Officer",
    "Sales Executive",
    "Graphic Designer",
    "Hotel Manager",
    "Receptionist",
    "Chef",
    "Waiter",
    "Electrician",
    "Plumber",
    "Driver",
    "Security Guard",
    "Store Manager",
    "Customer Support",
    "Data Entry Operator",
    "Office Assistant",
    "Business Analyst",
    "Project Manager",
    "DevOps Engineer",
    "Data Analyst",
    "UI/UX Designer",
    "Mobile App Developer",
    "Legal Officer",
    "Social Worker",
]

SKILL_POOL = [
    "Python", "JavaScript", "Java", "C#", "C++", "SQL", "R", "Go", "Ruby",
    "HTML", "CSS", "React", "Angular", "Vue", "Django", "Flask", "Spring",
    "Node.js", "Express", "Docker", "Kubernetes", "AWS", "Azure", "GCP",
    "Git", "Linux", "Agile", "Scrum", "Machine Learning", "Data Visualization",
    "Photoshop", "Illustrator", "Figma", "Adobe XD", "SEO", "Content Marketing",
    "Financial Modeling", "Accounting", "Project Planning", "AutoCAD", "MATLAB",
    "Electrical Design", "Civil Drafting", "Customer Service", "Salesforce",
]

# ---------------------------------------------------------------------------
# Helper utilities – all checks are idempotent.
# ---------------------------------------------------------------------------

def create_user(session, email, password, role):
    existing = session.query(User).filter_by(email=email).first()
    if existing:
        return existing
    user = User(email=email, role=role)
    user.set_password(password)
    session.add(user)
    session.flush()
    return user

def create_company(session, name, industry, admin_user):
    existing = session.query(Company).filter_by(name=name).first()
    if existing:
        return existing
    company = Company(
        name=name,
        industry=industry,
        email=f"contact@{name.lower().replace(' ', '').replace(',', '')}.com",
        website=f"https://www.{name.lower().replace(' ', '').replace(',', '')}.com",
        phone=fake.phone_number(),
        description=fake.paragraph(nb_sentences=4),
        address=f"{fake.street_address()}, {random.choice(NEPAL_LOCATIONS)}",
        logo_url="https://via.placeholder.com/150",
        hr_name=fake.name(),
        hr_position=random.choice(["HR Manager", "Talent Acquisition Lead", "Recruitment Specialist", "Hiring Coordinator"]),
        admin=admin_user,
    )
    session.add(company)
    session.flush()
    return company

def create_job_seeker(session, user):
    existing = session.query(JobSeeker).filter_by(user_id=user.id).first()
    if existing:
        return existing
    category = random.choice(JOB_SEEKER_CATEGORIES)
    skills = random.sample(SKILL_POOL, k=random.randint(5, 12))
    seeker = JobSeeker(
        user_id=user.id,
        full_name=fake.name(),
        phone=fake.phone_number(),
        location=random.choice(NEPAL_LOCATIONS),
        education=random.choice(["Bachelor's", "Master's", "PhD"]),
        university=f"{fake.company()} University",
        graduation_year=random.randint(2005, 2023),
        years_experience=random.randint(0, 12),
        current_position=category,
        expected_salary_npr=random.randint(300_000, 2_500_000),
        resume_summary=fake.sentence(nb_words=20),
        linkedin_url=f"https://www.linkedin.com/in/{fake.user_name()}",
        portfolio_url=(f"https://{fake.user_name()}.portfolio.com" if random.random() < 0.4 else None),
        profile_photo_url="https://via.placeholder.com/150",
        skills_json=json.dumps(skills),
    )
    session.add(seeker)
    session.flush()
    return seeker

def create_job(session, company):
    title_category = random.choice(JOB_TITLES)
    title = f"{title_category} – {fake.word().capitalize()}"
    required_skills = random.sample(SKILL_POOL, k=random.randint(5, 12))
    salary_min = random.randint(300_000, 800_000)
    salary_max = salary_min + random.randint(100_000, 500_000)
    job = Job(
        title=title,
        company_id=company.id,
        category=title_category,
        employment_type=random.choice(["Full-time", "Part-time", "Contract", "Internship"]),
        experience_required=random.choice(["Entry", "Mid", "Senior", "Lead"]),
        education_required=random.choice(["Bachelor's", "Master's", "PhD"]),
        location=random.choice(NEPAL_LOCATIONS),
        salary_min_npr=salary_min,
        salary_max_npr=salary_max,
        vacancies=random.randint(1, 5),
        description=fake.paragraph(nb_sentences=6),
        required_skills_json=json.dumps(required_skills),
        responsibilities="; ".join([fake.sentence() for _ in range(3)]),
        benefits=", ".join([random.choice(["Health Insurance", "Paid Time Off", "Retirement Plan", "Gym Membership", "Stock Options"]) for _ in range(3)]),
        posted_date=datetime.utcnow().date() - timedelta(days=random.randint(0, 30)),
        deadline=datetime.utcnow().date() + timedelta(days=random.randint(15, 60)),
        remote_status=random.choice(["Remote", "Hybrid", "On-site"]),
    )
    session.add(job)
    session.flush()
    return job

def create_application(session, seeker, job):
    exists = session.query(Application).filter_by(seeker_id=seeker.id, job_id=job.id).first()
    if exists:
        return exists
    status = random.choices(
        ["Applied", "Interviewed", "Shortlisted", "Rejected", "Hired"],
        weights=[45, 10, 15, 20, 10],
        k=1,
    )[0]
    app = Application(
        seeker_id=seeker.id,
        job_id=job.id,
        applied_at=datetime.utcnow() - timedelta(days=random.randint(0, 30)),
        status=status,
    )
    session.add(app)
    session.flush()
    return app

def create_saved_job(session, seeker, job):
    exists = session.query(SavedJob).filter_by(seeker_id=seeker.id, job_id=job.id).first()
    if exists:
        return exists
    saved = SavedJob(
        seeker_id=seeker.id,
        job_id=job.id,
        saved_at=datetime.utcnow() - timedelta(days=random.randint(0, 30)),
    )
    session.add(saved)
    session.flush()
    return saved

# ---------------------------------------------------------------------------
# Seeding routine – runs only when the DB is empty (no users present).
# ---------------------------------------------------------------------------

def main():
    print("✓ Connected to PostgreSQL")
    Base.metadata.create_all(engine)
    print("✓ Tables created")

    with Session() as session:
        if session.query(User).first():
            print("✅ Database already contains data – seeding skipped.")
            return

        # ----- Super Admin -----
        super_admin = create_user(session, "admin@careerswipe.com", "Password123!", "super_admin")
        print("✓ Users inserted (super admin)")

        # ----- Companies -----
        companies = []
        for i in range(15):
            comp_email = f"company{i+1}@example.com"
            comp_user = create_user(session, comp_email, "Password123!", "company_admin")
            company = create_company(
                session,
                name=f"{fake.company()} Ltd",
                industry=random.choice(COMPANY_INDUSTRIES),
                admin_user=comp_user,
            )
            companies.append(company)
        print("✓ Companies inserted")

        # ----- Job Seekers -----
        seekers = []
        for i in range(50):
            seeker_user = create_user(session, f"seeker{i+1}@example.com", "Password123!", "job_seeker")
            seeker = create_job_seeker(session, seeker_user)
            seekers.append(seeker)
        print("✓ Users inserted (job seekers)")

        # ----- Jobs -----
        jobs = []
        for i in range(100):
            company = random.choice(companies)
            job = create_job(session, company)
            jobs.append(job)
        print("✓ Jobs inserted")

        # ----- Applications & Saved Jobs -----
        for seeker in seekers:
            applied = random.sample(jobs, k=random.randint(3, 5))
            for job in applied:
                create_application(session, seeker, job)
            saved = random.sample([j for j in jobs if j not in applied], k=random.randint(0, 3))
            for job in saved:
                create_saved_job(session, seeker, job)
        print("✓ Applications inserted")
        print("✓ Saved Jobs inserted")

        # ----- Basic Notifications -----
        for user in session.query(User).all():
            notif = Notification(
                user_id=user.id,
                title="Welcome to CareerSwipe",
                message="Your demo account has been created. Enjoy exploring!",
            )
            session.add(notif)
        print("✓ Notifications inserted")

        session.commit()
        print("✓ Database seeded successfully")

if __name__ == "__main__":
    main()
