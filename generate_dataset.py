# -*- coding: utf-8 -*-
"""generate_dataset.py

A self‑contained script that creates a realistic mock data set for the CareerSwipe job portal.
It generates:
- 50 job seekers
- 50 companies
- 200 job postings
- Related entities (applications, saved jobs, interview invitations, etc.)

All data is written as SQL INSERT statements compatible with SQLite/MySQL/PostgreSQL.
The script relies only on the `faker` library (installed via pip) and the Python standard library.
"""

import random
import json
from datetime import datetime, timedelta
from pathlib import Path

from faker import Faker

fake = Faker()
Fake = Faker

# ---------------------------------------------------------------------------
# Configuration – tweak numbers here if you need a larger or smaller data set
# ---------------------------------------------------------------------------
NUM_JOB_SEEKERS = 50
NUM_COMPANIES = 50
NUM_JOBS = 200

# ---------------------------------------------------------------------------
# Static reference data
# ---------------------------------------------------------------------------
JOB_CATEGORIES = [
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

INDUSTRIES = [
    "IT",
    "Construction",
    "Banking",
    "Manufacturing",
    "Healthcare",
    "Education",
    "Logistics",
    "Marketing",
    "Telecommunications",
    "Retail",
]

EMPLOYMENT_TYPES = ["Full-time", "Part-time", "Contract", "Internship", "Temporary"]

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
# Helper functions
# ---------------------------------------------------------------------------
def random_date(start_days_ago=365, end_days_ago=0):
    """Return a random datetime between start_days_ago and end_days_ago days before today."""
    start = datetime.now() - timedelta(days=start_days_ago)
    end = datetime.now() - timedelta(days=end_days_ago)
    return fake.date_between(start_date=start, end_date=end)

def escape_sql(value: str) -> str:
    """Escape single quotes for safe insertion into a SQL string literal."""
    return value.replace("'", "''")

# ---------------------------------------------------------------------------
# Data generation
# ---------------------------------------------------------------------------
job_seekers = []
for _ in range(NUM_JOB_SEEKERS):
    category = random.choice(JOB_CATEGORIES)
    name = fake.name()
    email = fake.unique.email()
    phone = fake.phone_number()
    location = "Nepal"
    education = random.choice(["Bachelor's", "Master's", "PhD", "Associate"])
    university = fake.company() + " University"
    graduation_year = random.randint(2005, 2023)
    skills = random.sample(SKILL_POOL, k=random.randint(5, 15))
    years_exp = random.randint(0, 10)
    current_position = category
    expected_salary = random.randint(30000, 150000)
    resume_summary = fake.sentence(nb_words=15)
    linkedin = f"https://www.linkedin.com/in/{name.lower().replace(' ', '-') }"
    portfolio = f"https://{name.lower().replace(' ', '-') }.portfolio.com" if random.random() < 0.4 else None
    job_seekers.append({
        "full_name": name,
        "email": email,
        "phone": phone,
        "location": location,
        "education": education,
        "university": university,
        "grad_year": graduation_year,
        "skills": skills,
        "years_exp": years_exp,
        "current_position": current_position,
        "expected_salary": expected_salary,
        "resume_summary": resume_summary,
        "linkedin": linkedin,
        "portfolio": portfolio,
    })

companies = []
for _ in range(NUM_COMPANIES):
    industry = random.choice(INDUSTRIES)
    name = fake.company() + " Ltd"
    email = f"contact@{name.lower().replace(' ', '').replace(',', '')}.com"
    website = f"https://www.{name.lower().replace(' ', '').replace(',', '')}.com"
    phone = fake.phone_number()
    description = fake.paragraph(nb_sentences=3)
    hq_location = fake.city() + ", " + fake.country()
    num_employees = random.randint(20, 2000)
    size = "Small" if num_employees < 100 else "Medium" if num_employees < 500 else "Large"
    recruiter_name = fake.name()
    recruiter_position = random.choice(["HR Manager", "Talent Acquisition Lead", "Recruitment Specialist", "Hiring Coordinator"])
    companies.append({
        "name": name,
        "industry": industry,
        "email": email,
        "website": website,
        "phone": phone,
        "description": description,
        "hq_location": hq_location,
        "num_employees": num_employees,
        "size": size,
        "recruiter_name": recruiter_name,
        "recruiter_position": recruiter_position,
    })

jobs = []
for _ in range(NUM_JOBS):
    company = random.choice(companies)
    category = random.choice(JOB_CATEGORIES)
    title = f"{category} - {fake.word().capitalize()}"
    employment_type = random.choice(EMPLOYMENT_TYPES)
    exp_required = random.choice(["Entry", "Mid", "Senior", "Lead"])
    edu_required = random.choice(["Bachelor's", "Master's", "PhD"])
    location = random.choice(["Kathmandu", "Pokhara", "Biratnagar", "Remote", "Hybrid"])
    salary_min = random.randint(30000, 80000)
    salary_max = salary_min + random.randint(10000, 50000)
    vacancies = random.randint(1, 10)
    description = fake.paragraph(nb_sentences=5)
    required_skills = random.sample(SKILL_POOL, k=random.randint(5, 12))
    responsibilities = "; ".join([fake.sentence() for _ in range(3)])
    benefits = ", ".join([random.choice(["Health Insurance", "Paid Time Off", "Retirement Plan", "Gym Membership", "Stock Options"]) for _ in range(3)])
    posted_date = random_date(start_days_ago=180, end_days_ago=0)
    deadline = posted_date + timedelta(days=random.randint(15, 60))
    remote_status = random.choice(["Remote", "Hybrid", "On-site"])
    jobs.append({
        "title": title,
        "company_name": company["name"],
        "category": category,
        "employment_type": employment_type,
        "exp_required": exp_required,
        "edu_required": edu_required,
        "location": location,
        "salary_min": salary_min,
        "salary_max": salary_max,
        "vacancies": vacancies,
        "description": description,
        "required_skills": required_skills,
        "responsibilities": responsibilities,
        "benefits": benefits,
        "posted_date": posted_date.strftime('%Y-%m-%d'),
        "deadline": deadline.strftime('%Y-%m-%d'),
        "remote_status": remote_status,
    })

# ---------------------------------------------------------------------------
# Relationship generation – applications, saved jobs, etc.
# ---------------------------------------------------------------------------
applications = []
saved_jobs = []
interview_invitations = []
shortlisted = []
rejected = []
hired = []

application_id = 1
for seeker in job_seekers:
    # Each seeker applies to 3‑8 random jobs
    applied_jobs = random.sample(jobs, k=random.randint(3, 8))
    for job in applied_jobs:
        app_date = random_date(start_days_ago=120, end_days_ago=0)
        status = random.choices(
            ["Applied", "Interviewed", "Shortlisted", "Rejected", "Hired"],
            weights=[40, 15, 15, 20, 10],
            k=1,
        )[0]
        applications.append({
            "app_id": application_id,
            "seeker_email": seeker["email"],
            "job_title": job["title"],
            "company_name": job["company_name"],
            "application_date": app_date.strftime('%Y-%m-%d'),
            "status": status,
        })
        if status == "Interviewed":
            interview_invitations.append({
                "app_id": application_id,
                "interview_date": (app_date + timedelta(days=random.randint(7, 21))).strftime('%Y-%m-%d'),
                "mode": random.choice(["In‑person", "Video Call", "Phone"]),
            })
        elif status == "Shortlisted":
            shortlisted.append(application_id)
        elif status == "Rejected":
            rejected.append(application_id)
        elif status == "Hired":
            hired.append(application_id)
        application_id += 1
    # Saved jobs – random subset of jobs not applied to
    saved = random.sample([j for j in jobs if j not in applied_jobs], k=random.randint(0, 5))
    for job in saved:
        saved_jobs.append({
            "seeker_email": seeker["email"],
            "job_title": job["title"],
            "company_name": job["company_name"],
            "saved_date": random_date(start_days_ago=90, end_days_ago=0).strftime('%Y-%m-%d'),
        })

# ---------------------------------------------------------------------------
# SQL generation
# ---------------------------------------------------------------------------
output_lines = []

# Job seekers
output_lines.append("-- Job Seekers")
for js in job_seekers:
    skills_json = json.dumps(js["skills"]).replace('"', "'")
    portfolio_val = f"'{escape_sql(js['portfolio'])}'" if js["portfolio"] else "NULL"
    output_lines.append(
        f"INSERT INTO job_seekers (full_name, email, phone, location, education, university, graduation_year, skills, years_experience, current_position, expected_salary, resume_summary, linkedin_url, portfolio_url) VALUES ("
        f"'{escape_sql(js['full_name'])}', '{escape_sql(js['email'])}', '{escape_sql(js['phone'])}', '{escape_sql(js['location'])}', '{escape_sql(js['education'])}', '{escape_sql(js['university'])}', {js['grad_year']}, '{skills_json}', {js['years_exp']}, '{escape_sql(js['current_position'])}', {js['expected_salary']}, '{escape_sql(js['resume_summary'])}', '{escape_sql(js['linkedin'])}', {portfolio_val});"
    )

# Companies
output_lines.append("\n-- Companies")
for co in companies:
    output_lines.append(
        f"INSERT INTO companies (name, industry, email, website, phone, description, headquarters_location, employee_count, size, recruiter_name, recruiter_position) VALUES ("
        f"'{escape_sql(co['name'])}', '{escape_sql(co['industry'])}', '{escape_sql(co['email'])}', '{escape_sql(co['website'])}', '{escape_sql(co['phone'])}', '{escape_sql(co['description'])}', '{escape_sql(co['hq_location'])}', {co['num_employees']}, '{escape_sql(co['size'])}', '{escape_sql(co['recruiter_name'])}', '{escape_sql(co['recruiter_position'])}');"
    )

# Jobs
output_lines.append("\n-- Jobs")
for job in jobs:
    skills_json = json.dumps(job["required_skills"]).replace('"', "'")
    output_lines.append(
        f"INSERT INTO jobs (title, company_name, category, employment_type, experience_required, education_required, location, salary_min, salary_max, vacancies, description, required_skills, responsibilities, benefits, posted_date, application_deadline, remote_status) VALUES ("
        f"'{escape_sql(job['title'])}', '{escape_sql(job['company_name'])}', '{escape_sql(job['category'])}', '{escape_sql(job['employment_type'])}', '{escape_sql(job['exp_required'])}', '{escape_sql(job['edu_required'])}', '{escape_sql(job['location'])}', {job['salary_min']}, {job['salary_max']}, {job['vacancies']}, '{escape_sql(job['description'])}', '{skills_json}', '{escape_sql(job['responsibilities'])}', '{escape_sql(job['benefits'])}', '{job['posted_date']}', '{job['deadline']}', '{escape_sql(job['remote_status'])}');"
    )

# Applications
output_lines.append("\n-- Applications")
for app in applications:
    output_lines.append(
        f"INSERT INTO applications (application_id, seeker_email, job_title, company_name, application_date, status) VALUES ("
        f"{app['app_id']}, '{escape_sql(app['seeker_email'])}', '{escape_sql(app['job_title'])}', '{escape_sql(app['company_name'])}', '{app['application_date']}', '{app['status']}');"
    )

# Saved Jobs
output_lines.append("\n-- Saved Jobs")
for sv in saved_jobs:
    output_lines.append(
        f"INSERT INTO saved_jobs (seeker_email, job_title, company_name, saved_date) VALUES ("
        f"'{escape_sql(sv['seeker_email'])}', '{escape_sql(sv['job_title'])}', '{escape_sql(sv['company_name'])}', '{sv['saved_date']}');"
    )

# Interview Invitations
output_lines.append("\n-- Interview Invitations")
for inv in interview_invitations:
    output_lines.append(
        f"INSERT INTO interview_invitations (application_id, interview_date, mode) VALUES ("
        f"{inv['app_id']}, '{inv['interview_date']}', '{inv['mode']}');"
    )

# Shortlisted Candidates
output_lines.append("\n-- Shortlisted Candidates")
for sid in shortlisted:
    output_lines.append(f"INSERT INTO shortlisted_candidates (application_id) VALUES ({sid});")

# Rejected Candidates
output_lines.append("\n-- Rejected Candidates")
for rid in rejected:
    output_lines.append(f"INSERT INTO rejected_candidates (application_id) VALUES ({rid});")

# Hired Candidates
output_lines.append("\n-- Hired Candidates")
for hid in hired:
    output_lines.append(f"INSERT INTO hired_candidates (application_id) VALUES ({hid});")

# ---------------------------------------------------------------------------
# Write to file
# ---------------------------------------------------------------------------
output_path = Path('c:/Users/hp/Desktop/Career_swipe/dataset.sql')
output_path.write_text('\n'.join(output_lines), encoding='utf-8')
print(f"Dataset generated: {output_path}")

