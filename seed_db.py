from __future__ import annotations

from datetime import UTC, datetime, timedelta
from itertools import cycle

from app import app
from extensions import db
from models import (
    Company,
    JobListing,
    JobSwipe,
    RecommendationHistory,
    RecentlyViewedJob,
    SavedJob,
    Seeker,
    UploadedResume,
)
from werkzeug.security import generate_password_hash


DEMO_COMPANY_DOMAIN = "@careerswipe-demo.test"
DEMO_SEEKER_DOMAIN = "@demo.careerswipe.test"
DEMO_JOB_TAG = "careerswipe-nepal-demo"
DEMO_PASSWORD = "password123"

NEPAL_CITIES = [
    "Kathmandu",
    "Lalitpur",
    "Bhaktapur",
    "Pokhara",
    "Biratnagar",
    "Bharatpur",
    "Butwal",
    "Dharan",
    "Nepalgunj",
    "Hetauda",
    "Janakpur",
    "Dhangadhi",
]


def utcnow() -> datetime:
    return datetime.now(UTC).replace(tzinfo=None)


def slug(value: str) -> str:
    return "-".join("".join(ch.lower() if ch.isalnum() else " " for ch in value).split())


def phone(index: int) -> str:
    prefixes = ["980", "981", "984", "985", "986", "974", "976"]
    return f"+977-{prefixes[index % len(prefixes)]}-{4100000 + (index * 3791) % 5899999:07d}"


NEPAL_COMPANIES = [
    ("Himalayan Cloud Works", "Technology & IT", "Naxal, Kathmandu, Nepal", "https://himalayancloudworks.com"),
    ("MeroCode Solutions", "Technology & IT", "Jawalakhel, Lalitpur, Nepal", "https://merocode.com.np"),
    ("Kathmandu Data Lab", "Technology & IT", "New Baneshwor, Kathmandu, Nepal", "https://kathmandudatalab.com"),
    ("Sajilo Cyber Security", "Technology & IT", "Bhaktapur, Nepal", "https://sajilocyber.com"),
    ("Norvic Community Hospital", "Healthcare", "Thapathali, Kathmandu, Nepal", "https://norviccommunity.example.com"),
    ("Pokhara Wellness Clinic", "Healthcare", "Lakeside, Pokhara, Nepal", "https://pokharawellness.com"),
    ("Birat Medical Services", "Healthcare", "Biratnagar, Nepal", "https://biratmedical.com.np"),
    ("Bharatpur Diagnostic Center", "Healthcare", "Bharatpur, Nepal", "https://bharatpurdiagnostic.com"),
    ("Everest Academy Network", "Education", "Koteshwor, Kathmandu, Nepal", "https://everestacademy.edu.np"),
    ("Lumbini Technical College", "Education", "Butwal, Nepal", "https://lumbinitech.edu.np"),
    ("Janakpur Learning Hub", "Education", "Janakpur, Nepal", "https://janakpurlearning.edu.np"),
    ("Dhangadhi Model School", "Education", "Dhangadhi, Nepal", "https://dhangadhimodel.edu.np"),
    ("UrbanBuild Nepal", "Engineering", "Kupondole, Lalitpur, Nepal", "https://urbanbuild.com.np"),
    ("Hetauda Mechanical Works", "Engineering", "Hetauda, Nepal", "https://hetaudamechanical.com"),
    ("Dharan Infrastructure Partners", "Engineering", "Dharan, Nepal", "https://dharaninfra.com.np"),
    ("Valley Architecture Studio", "Engineering", "Kathmandu, Nepal", "https://valleyarchitecture.com.np"),
    ("Himalayan Finance Ltd.", "Banking & Finance", "Kamaladi, Kathmandu, Nepal", "https://himalayanfinance.com.np"),
    ("Nepalgunj Cooperative Bank", "Banking & Finance", "Nepalgunj, Nepal", "https://nepalgunjcoopbank.com"),
    ("Madhesh Investment Partners", "Banking & Finance", "Janakpur, Nepal", "https://madheshinvestment.com"),
    ("Pragati Audit Associates", "Banking & Finance", "Lalitpur, Nepal", "https://pragatiaudit.com.np"),
    ("PeopleFirst HR Nepal", "Business & Management", "Kathmandu, Nepal", "https://peoplefirsthr.com.np"),
    ("Koshi Project Services", "Business & Management", "Biratnagar, Nepal", "https://koshiprojects.com"),
    ("Summit Operations Group", "Business & Management", "Pokhara, Nepal", "https://summitoperations.com.np"),
    ("Naya Bazaar Consulting", "Business & Management", "Bharatpur, Nepal", "https://nayabazaarconsulting.com"),
    ("BrandMandu Media", "Sales & Marketing", "Pulchowk, Lalitpur, Nepal", "https://brandmandu.com"),
    ("Kantipur Growth Agency", "Sales & Marketing", "Kathmandu, Nepal", "https://kantipurgrowth.com"),
    ("Digital Chautari", "Sales & Marketing", "Bhaktapur, Nepal", "https://digitalchautari.com"),
    ("Gandaki Hospitality Group", "Hospitality & Tourism", "Pokhara, Nepal", "https://gandakihospitality.com"),
    ("Kathmandu Heritage Hotel", "Hospitality & Tourism", "Thamel, Kathmandu, Nepal", "https://kathmanduheritagehotel.com"),
    ("Terai Travel Services", "Hospitality & Tourism", "Bharatpur, Nepal", "https://teraitravel.com.np"),
    ("Hetauda Food Products", "Manufacturing & Production", "Hetauda, Nepal", "https://hetaudafoods.com"),
    ("Butwal Garments Factory", "Manufacturing & Production", "Butwal, Nepal", "https://butwalgarments.com.np"),
    ("Nepal Buildcon Pvt. Ltd.", "Construction", "Kathmandu, Nepal", "https://nepalbuildcon.com"),
    ("Sudurpaschim Construction", "Construction", "Dhangadhi, Nepal", "https://sudurpaschimbuild.com"),
    ("GreenTerai Agro", "Agriculture", "Chitwan Road, Bharatpur, Nepal", "https://greenteraiagro.com"),
    ("Koshi Vet & Farm Services", "Agriculture", "Biratnagar, Nepal", "https://koshivetfarm.com"),
    ("FastTrack Logistics Nepal", "Logistics & Transportation", "Balaju, Kathmandu, Nepal", "https://fasttracklogistics.com.np"),
    ("Lumbini Supply Chain", "Logistics & Transportation", "Butwal, Nepal", "https://lumbinisupplychain.com"),
    ("Nepal Legal Partners", "Legal", "Babarmahal, Kathmandu, Nepal", "https://nepallegalpartners.com"),
    ("Sajha Samaj NGO", "Government & NGOs", "Lalitpur, Nepal", "https://sajhasamaj.org.np"),
    ("Himal Media House", "Media & Creative", "Kathmandu, Nepal", "https://himalmediahouse.com"),
    ("Creative Pokhara Studio", "Media & Creative", "Pokhara, Nepal", "https://creativepokhara.studio"),
    ("CareConnect Nepal", "Customer Service", "Kathmandu, Nepal", "https://careconnect.com.np"),
    ("Dharan Retail Mart", "Retail", "Dharan, Nepal", "https://dharanretailmart.com"),
    ("Secure Valley Services", "Security", "Lalitpur, Nepal", "https://securevalley.com.np"),
    ("SkillSewa Nepal", "Other", "Kathmandu, Nepal", "https://skillsewa.com.np"),
]


ROLE_TITLES = {
    "Technology & IT": [
        "Software Engineer",
        "QA Engineer",
        "Frontend Developer",
        "Backend Developer",
        "Full Stack Developer",
        "DevOps Engineer",
        "Data Analyst",
        "UI/UX Designer",
        "Cybersecurity Analyst",
    ],
    "Healthcare": [
        "Doctor",
        "Nurse",
        "Pharmacist",
        "Lab Technician",
        "Radiologist",
        "Physiotherapist",
        "Medical Officer",
        "Health Assistant",
    ],
    "Education": [
        "School Teacher",
        "Lecturer",
        "Professor",
        "Principal",
        "Teaching Assistant",
        "Academic Coordinator",
    ],
    "Engineering": [
        "Civil Engineer",
        "Mechanical Engineer",
        "Electrical Engineer",
        "Architect",
        "Survey Engineer",
        "Structural Engineer",
    ],
    "Banking & Finance": [
        "Accountant",
        "Financial Analyst",
        "Bank Teller",
        "Loan Officer",
        "Internal Auditor",
        "Investment Officer",
        "Finance Manager",
    ],
    "Business & Management": [
        "HR Officer",
        "HR Manager",
        "Project Manager",
        "Business Analyst",
        "Operations Manager",
        "Office Administrator",
    ],
    "Sales & Marketing": [
        "Sales Executive",
        "Marketing Officer",
        "Digital Marketing Specialist",
        "SEO Specialist",
        "Social Media Manager",
        "Brand Manager",
    ],
    "Hospitality & Tourism": [
        "Hotel Manager",
        "Receptionist",
        "Chef",
        "Waiter/Waitress",
        "Travel Consultant",
        "Tour Guide",
        "Housekeeping Supervisor",
    ],
    "Manufacturing & Production": [
        "Production Supervisor",
        "Quality Inspector",
        "Factory Manager",
        "Machine Operator",
    ],
    "Construction": [
        "Site Engineer",
        "Construction Supervisor",
        "Quantity Surveyor",
        "Safety Officer",
    ],
    "Agriculture": [
        "Agriculture Officer",
        "Veterinary Technician",
        "Farm Manager",
        "Agricultural Research Assistant",
    ],
    "Logistics & Transportation": [
        "Driver",
        "Delivery Officer",
        "Warehouse Manager",
        "Logistics Coordinator",
        "Supply Chain Officer",
    ],
    "Legal": [
        "Lawyer",
        "Legal Officer",
        "Paralegal",
        "Compliance Officer",
    ],
    "Government & NGOs": [
        "Program Officer",
        "Field Officer",
        "Social Worker",
        "Community Development Officer",
        "Monitoring & Evaluation Officer",
    ],
    "Media & Creative": [
        "Graphic Designer",
        "Video Editor",
        "Photographer",
        "Journalist",
        "Content Writer",
        "Animator",
    ],
    "Customer Service": [
        "Customer Support Executive",
        "Call Center Representative",
        "Client Relationship Officer",
    ],
    "Retail": [
        "Store Manager",
        "Cashier",
        "Sales Associate",
        "Inventory Officer",
    ],
    "Security": [
        "Security Officer",
        "CCTV Operator",
        "Security Supervisor",
    ],
    "Other": [
        "Electrician",
        "Plumber",
        "Carpenter",
        "Tailor",
        "Beautician",
        "Fitness Trainer",
        "Event Coordinator",
    ],
}


INDUSTRY_DETAILS = {
    "Technology & IT": {
        "skills": ["Python", "JavaScript", "SQL", "Git", "Testing", "Cloud", "APIs", "Linux", "Security", "Agile"],
        "education": "Bachelor in Computer Science, IT, Software Engineering, or equivalent experience",
        "benefits": "Health insurance, learning budget, hybrid work options, festival bonus",
        "salary": (55000, 180000),
    },
    "Healthcare": {
        "skills": ["Patient Care", "Clinical Assessment", "Medical Records", "Infection Control", "Team Coordination", "Nepal Health Guidelines"],
        "education": "Relevant medical, nursing, pharmacy, lab, or health science qualification with valid council registration where required",
        "benefits": "Health coverage, duty meal, paid leave, training support, shift allowance",
        "salary": (30000, 160000),
    },
    "Education": {
        "skills": ["Lesson Planning", "Student Assessment", "Classroom Management", "Curriculum Delivery", "Parent Communication", "Digital Learning Tools"],
        "education": "Bachelor or Master degree in relevant subject; teaching license preferred for school roles",
        "benefits": "Provident fund, paid school holidays, professional development, lunch allowance",
        "salary": (28000, 140000),
    },
    "Engineering": {
        "skills": ["AutoCAD", "Project Planning", "Site Coordination", "Technical Drawing", "Quality Control", "Safety Compliance"],
        "education": "Bachelor or diploma in relevant engineering discipline; Nepal Engineering Council registration preferred",
        "benefits": "Site allowance, accident insurance, training support, performance bonus",
        "salary": (45000, 170000),
    },
    "Banking & Finance": {
        "skills": ["Accounting", "Excel", "Financial Reporting", "Risk Review", "Customer Service", "Compliance", "Reconciliation"],
        "education": "Bachelor in Management, Finance, Accounting, Economics, or related field",
        "benefits": "Provident fund, insurance, performance incentive, training and certification support",
        "salary": (32000, 150000),
    },
    "Business & Management": {
        "skills": ["Planning", "Reporting", "Stakeholder Management", "Documentation", "Excel", "Communication", "Process Improvement"],
        "education": "Bachelor in Management, Business Administration, Public Administration, or related field",
        "benefits": "Health insurance, paid leave, festival bonus, leadership training",
        "salary": (35000, 160000),
    },
    "Sales & Marketing": {
        "skills": ["Lead Generation", "CRM", "Communication", "Campaign Planning", "Digital Marketing", "Negotiation", "Reporting"],
        "education": "Bachelor in Marketing, Business, Communications, or equivalent practical experience",
        "benefits": "Sales incentive, travel allowance, phone allowance, training support",
        "salary": (28000, 130000),
    },
    "Hospitality & Tourism": {
        "skills": ["Guest Service", "Reservation Handling", "Food Safety", "Team Coordination", "Communication", "Tour Planning"],
        "education": "Hotel management, tourism, culinary, or relevant vocational training preferred",
        "benefits": "Service charge, meal, uniform, shift allowance, accommodation support where applicable",
        "salary": (22000, 120000),
    },
    "Manufacturing & Production": {
        "skills": ["Production Planning", "Quality Control", "Machine Operation", "Safety Compliance", "Inventory Tracking", "Shift Supervision"],
        "education": "Diploma, technical training, or relevant production experience",
        "benefits": "Overtime pay, meal, uniform, accident insurance, festival bonus",
        "salary": (25000, 110000),
    },
    "Construction": {
        "skills": ["Site Supervision", "BOQ", "Construction Safety", "Vendor Coordination", "Measurement", "Quality Control"],
        "education": "Civil engineering, construction management, safety training, or related technical qualification",
        "benefits": "Site allowance, travel support, accident insurance, paid leave",
        "salary": (35000, 150000),
    },
    "Agriculture": {
        "skills": ["Farm Planning", "Crop Management", "Livestock Care", "Field Reporting", "Community Training", "Data Collection"],
        "education": "Agriculture, veterinary, animal science, or rural development qualification preferred",
        "benefits": "Field allowance, travel support, insurance, technical training",
        "salary": (26000, 100000),
    },
    "Logistics & Transportation": {
        "skills": ["Route Planning", "Inventory Control", "Dispatch", "Documentation", "Customer Handling", "Safety Compliance"],
        "education": "SEE/SLC to Bachelor depending on role; valid driving license required for driver roles",
        "benefits": "Fuel or travel allowance, overtime pay, insurance, mobile allowance",
        "salary": (24000, 115000),
    },
    "Legal": {
        "skills": ["Legal Research", "Drafting", "Compliance", "Case Documentation", "Negotiation", "Regulatory Review"],
        "education": "LLB or related legal qualification; Nepal Bar Council license required for lawyer roles",
        "benefits": "Professional membership support, insurance, paid leave, research allowance",
        "salary": (35000, 160000),
    },
    "Government & NGOs": {
        "skills": ["Field Mobilization", "Report Writing", "Monitoring", "Community Engagement", "Data Collection", "Safeguarding"],
        "education": "Bachelor in Social Work, Development Studies, Public Health, Agriculture, or relevant field",
        "benefits": "Field allowance, insurance, communication allowance, learning opportunities",
        "salary": (30000, 130000),
    },
    "Media & Creative": {
        "skills": ["Content Planning", "Adobe Creative Suite", "Storytelling", "Editing", "Photography", "Social Media"],
        "education": "Media studies, design, journalism, animation, or strong portfolio-based experience",
        "benefits": "Creative equipment access, flexible schedule, project bonus, training support",
        "salary": (28000, 125000),
    },
    "Customer Service": {
        "skills": ["Customer Support", "CRM", "Call Handling", "Email Support", "Conflict Resolution", "Documentation"],
        "education": "Plus Two or Bachelor degree with strong communication skills",
        "benefits": "Shift allowance, performance incentive, training, health insurance",
        "salary": (24000, 85000),
    },
    "Retail": {
        "skills": ["POS Handling", "Inventory Control", "Customer Service", "Merchandising", "Cash Handling", "Sales Reporting"],
        "education": "SEE/SLC, Plus Two, or Bachelor depending on role",
        "benefits": "Sales incentive, meal allowance, uniform, festival bonus",
        "salary": (22000, 90000),
    },
    "Security": {
        "skills": ["Access Control", "CCTV Monitoring", "Incident Reporting", "Emergency Response", "Patrolling", "Visitor Management"],
        "education": "SEE/SLC preferred; security training or ex-service background valued",
        "benefits": "Uniform, duty meal, overtime pay, insurance, shift allowance",
        "salary": (22000, 80000),
    },
    "Other": {
        "skills": ["Technical Service", "Customer Handling", "Tool Handling", "Scheduling", "Safety Practices", "Quality Workmanship"],
        "education": "Vocational training, apprenticeship, or proven practical experience",
        "benefits": "Tools support, travel allowance, overtime pay, skill training",
        "salary": (22000, 95000),
    },
}


def company_description(name: str, industry: str, address: str) -> str:
    city = next((city for city in NEPAL_CITIES if city in address), "Nepal")
    return (
        f"{name} is a Nepal-based {industry.lower()} employer operating from {city}. "
        "The company focuses on dependable service delivery, ethical hiring, practical training, "
        "and long-term career growth for local professionals."
    )


def experience_for(title: str) -> tuple[str, str, int]:
    senior_words = ["Manager", "Principal", "Professor", "Radiologist", "Doctor", "Finance Manager", "Factory Manager"]
    entry_words = ["Assistant", "Teller", "Cashier", "Waiter", "Driver", "Operator", "Representative", "Associate"]
    if any(word in title for word in senior_words):
        return "Senior Level", "5-8 years", 5
    if any(word in title for word in entry_words):
        return "Entry Level", "0-2 years", 0
    return "Mid Level", "2-4 years", 2


def salary_range(industry: str, index: int, min_exp: int) -> tuple[int, int, str]:
    base_min, base_max = INDUSTRY_DETAILS[industry]["salary"]
    low = base_min + (index % 5) * 5000 + min_exp * 6000
    high = min(base_max, low + 25000 + (index % 4) * 10000)
    if high <= low:
        high = low + 20000
    return low, high, f"NPR {low:,} - {high:,} per month"


def job_description(title: str, company: Company, industry: str, education: str, deadline: datetime) -> str:
    details = INDUSTRY_DETAILS[industry]
    responsibilities = [
        f"Deliver day-to-day {title.lower()} work according to company standards.",
        "Coordinate with team members, supervisors, clients, and field partners as needed.",
        "Maintain accurate records, reports, and documentation for assigned work.",
        "Follow Nepal compliance, safety, and service quality requirements relevant to the role.",
    ]
    return "\n".join(
        [
            f"{company.company_name} is hiring a {title} for its Nepal operations.",
            f"Industry: {industry}",
            f"Education Requirement: {education}",
            "Responsibilities:",
            *[f"- {item}" for item in responsibilities],
            f"Benefits: {details['benefits']}",
            f"Application Deadline: {deadline.strftime('%Y-%m-%d')}",
        ]
    )


def delete_jobs(jobs: list[JobListing]) -> int:
    job_ids = [job.id for job in jobs if job.id is not None]
    if not job_ids:
        return 0
    SavedJob.query.filter(SavedJob.job_id.in_(job_ids)).delete(synchronize_session=False)
    RecentlyViewedJob.query.filter(RecentlyViewedJob.job_id.in_(job_ids)).delete(synchronize_session=False)
    RecommendationHistory.query.filter(RecommendationHistory.job_id.in_(job_ids)).delete(synchronize_session=False)
    JobSwipe.query.filter(JobSwipe.job_id.in_(job_ids)).delete(synchronize_session=False)
    for job in jobs:
        db.session.delete(job)
    return len(job_ids)


def delete_seekers(seekers: list[Seeker]) -> int:
    seeker_ids = [seeker.id for seeker in seekers if seeker.id is not None]
    if not seeker_ids:
        return 0
    SavedJob.query.filter(SavedJob.seeker_id.in_(seeker_ids)).delete(synchronize_session=False)
    RecentlyViewedJob.query.filter(RecentlyViewedJob.seeker_id.in_(seeker_ids)).delete(synchronize_session=False)
    RecommendationHistory.query.filter(RecommendationHistory.seeker_id.in_(seeker_ids)).delete(synchronize_session=False)
    JobSwipe.query.filter(JobSwipe.seeker_id.in_(seeker_ids)).delete(synchronize_session=False)
    UploadedResume.query.filter(UploadedResume.seeker_id.in_(seeker_ids)).delete(synchronize_session=False)
    for seeker in seekers:
        db.session.delete(seeker)
    return len(seeker_ids)


def is_nepal_text(value: str | None) -> bool:
    text = (value or "").lower()
    return "nepal" in text or any(city.lower() in text for city in NEPAL_CITIES)


def is_allowed_job_location(value: str | None) -> bool:
    text = (value or "").lower()
    return any(city.lower() in text for city in NEPAL_CITIES)


def cleanup_non_nepal_demo_data() -> tuple[int, int, int]:
    demo_companies = Company.query.filter(Company.email.like(f"%{DEMO_COMPANY_DOMAIN}")).all()
    valid_seed_emails = {f"careers.{slug(name)}{DEMO_COMPANY_DOMAIN}" for name, _, _, _ in NEPAL_COMPANIES}
    non_nepal_companies = [
        company
        for company in demo_companies
        if company.email not in valid_seed_emails and not is_nepal_text(company.company_address)
    ]
    non_nepal_company_ids = {company.id for company in non_nepal_companies}

    demo_jobs = (
        JobListing.query.join(Company)
        .filter(Company.email.like(f"%{DEMO_COMPANY_DOMAIN}"))
        .all()
    )
    non_nepal_jobs = [
        job
        for job in demo_jobs
        if job.company_id not in non_nepal_company_ids and not is_allowed_job_location(job.location)
    ]
    removed_jobs = delete_jobs(non_nepal_jobs)

    for company in non_nepal_companies:
        delete_jobs(list(company.jobs))
        db.session.delete(company)

    demo_seekers = Seeker.query.filter(Seeker.email.like(f"%{DEMO_SEEKER_DOMAIN}")).all()
    non_nepal_seekers = [
        seeker
        for seeker in demo_seekers
        if not is_nepal_text(seeker.address) and (seeker.country or "").lower() != "nepal"
    ]
    removed_seekers = delete_seekers(non_nepal_seekers)
    return removed_jobs, len(non_nepal_companies), removed_seekers


def upsert_companies() -> list[Company]:
    password_hash = generate_password_hash(DEMO_PASSWORD)
    companies: list[Company] = []
    for index, (name, industry, address, website) in enumerate(NEPAL_COMPANIES, start=1):
        email = f"careers.{slug(name)}{DEMO_COMPANY_DOMAIN}"
        company = Company.query.filter_by(email=email).first()
        if company is None:
            company = Company(email=email, password_hash=password_hash)
            db.session.add(company)

        company.company_name = name
        company.phone = phone(index)
        company.hr_name = f"HR Team {name.split()[0]}"
        company.company_address = address
        company.headquarters = address
        company.description = company_description(name, industry, address)
        company.mission = f"To build reliable {industry.lower()} services and employment opportunities in Nepal."
        company.vision = "To be a trusted Nepal employer known for inclusive teams and practical career growth."
        company.culture = "Professional, inclusive, accountable, and learning-oriented"
        company.perks = "Paid leave, festival bonus, insurance options, training support"
        company.industry = industry
        company.company_type = "Private Limited" if industry not in {"Government & NGOs", "Education"} else "Institution"
        company.company_size = ["11-50", "51-200", "201-500", "501-1000"][index % 4]
        company.founded_year = 2005 + (index % 18)
        company.website = website
        company.hiring_frequency = "Quarterly"
        company.remote_hiring = industry in {"Technology & IT", "Media & Creative", "Customer Service"}
        company.international_hiring = False
        company.preferred_locations = ", ".join(NEPAL_CITIES)
        company.hiring_categories = industry
        company.work_mode = "Hybrid" if company.remote_hiring else "Onsite"
        company.open_positions = ", ".join(ROLE_TITLES[industry][:5])
        company.number_of_vacancies = 2 + (index % 12)
        company.linkedin_url = f"https://linkedin.com/company/{slug(name)}"
        company.business_registration = f"NEPAL-DEMO-2026-{index:04d}"
        company.profile_completion = 96
        company.is_published = True
        company.is_verified = True
        company.age_verified = True
        company.legally_eligible = True
        company.country = "Nepal"
        if company.created_at is None:
            company.created_at = utcnow() - timedelta(days=120 + index)
        companies.append(company)
    db.session.commit()
    return companies


def build_job_specs(companies: list[Company]) -> list[dict]:
    companies_by_industry: dict[str, list[Company]] = {}
    for company in companies:
        companies_by_industry.setdefault(company.industry, []).append(company)

    specs = []
    city_cycle = cycle(NEPAL_CITIES)
    for industry, titles in ROLE_TITLES.items():
        company_cycle = cycle(companies_by_industry[industry])
        for title in titles:
            company = next(company_cycle)
            city = next(city_cycle)
            specs.append({"industry": industry, "title": title, "company": company, "city": city})
    return specs


def upsert_jobs(companies: list[Company]) -> tuple[int, int]:
    created = 0
    updated = 0
    for index, spec in enumerate(build_job_specs(companies), start=1):
        company = spec["company"]
        title = spec["title"]
        industry = spec["industry"]
        city = spec["city"]
        details = INDUSTRY_DETAILS[industry]
        experience_level, experience_required, min_exp = experience_for(title)
        low, high, salary = salary_range(industry, index, min_exp)
        deadline = utcnow() + timedelta(days=21 + (index % 35))
        seed_id = f"{DEMO_JOB_TAG}:{slug(company.company_name)}:{slug(title)}:{slug(city)}"

        job = JobListing.query.filter(JobListing.tags.like(f"%{seed_id}%")).first()
        if job is None:
            job = (
                JobListing.query.filter_by(company_id=company.id, title=title, location=f"{city}, Nepal")
                .first()
            )
        if job is None:
            job = JobListing(company_id=company.id, title=title, location=f"{city}, Nepal")
            db.session.add(job)
            created += 1
        else:
            updated += 1

        education = details["education"]
        skills = details["skills"]
        job.company_id = company.id
        job.title = title
        job.location = f"{city}, Nepal"
        job.job_type = "Remote" if industry in {"Technology & IT", "Media & Creative", "Customer Service"} and index % 5 == 0 else (
            "Internship" if "Assistant" in title and index % 2 == 0 else "Full-time"
        )
        job.job_location_type = "Remote" if job.job_type == "Remote" else ("Hybrid" if industry in {"Technology & IT", "Sales & Marketing", "Business & Management"} and index % 3 == 0 else "Onsite")
        job.experience_level = experience_level
        job.min_experience = min_exp
        job.experience_required = experience_required
        job.salary = salary
        job.max_salary = high
        job.required_skills = ", ".join(skills)
        job.description = job_description(title, company, industry, education, deadline)
        job.tags = ", ".join(
            [
                seed_id,
                DEMO_JOB_TAG,
                "Nepal",
                city,
                industry,
                title,
                education,
                *skills,
            ]
        )
        job.is_boosted = index % 11 == 0
        if job.created_at is None:
            job.created_at = utcnow() - timedelta(days=index % 60)
    db.session.commit()
    return created, updated


def seed() -> None:
    with app.app_context():
        removed_jobs, removed_companies, removed_seekers = cleanup_non_nepal_demo_data()
        db.session.commit()

        companies = upsert_companies()
        created_jobs, updated_jobs = upsert_jobs(companies)

        total_demo_companies = Company.query.filter(Company.email.like(f"%{DEMO_COMPANY_DOMAIN}")).count()
        total_nepal_demo_jobs = (
            JobListing.query.join(Company)
            .filter(Company.email.like(f"%{DEMO_COMPANY_DOMAIN}"))
            .filter(JobListing.location.like("%Nepal%"))
            .count()
        )
        industries = sorted({company.industry for company in companies})

        print("CareerSwipe Nepal demo seed complete")
        print(f"Removed non-Nepal demo jobs: {removed_jobs}")
        print(f"Removed non-Nepal demo companies: {removed_companies}")
        print(f"Removed non-Nepal demo seekers: {removed_seekers}")
        print(f"Demo companies available: {total_demo_companies}")
        print(f"Nepal demo jobs available: {total_nepal_demo_jobs}")
        print(f"Jobs created this run: {created_jobs}")
        print(f"Jobs updated this run: {updated_jobs}")
        print(f"Industries covered: {', '.join(industries)}")
        print(f"Demo company password: {DEMO_PASSWORD}")


if __name__ == "__main__":
    seed()
