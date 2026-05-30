from app import app
from extensions import db
from models import Company, JobListing, JobSwipe, Notification, Seeker
from werkzeug.security import generate_password_hash
import uuid


with app.app_context():
    email = "codex_" + uuid.uuid4().hex[:8] + "@example.com"
    co_email = "codex_co_" + uuid.uuid4().hex[:8] + "@example.com"
    seeker = Seeker(
        first_name="Codex",
        last_name="Tester",
        email=email,
        password_hash=generate_password_hash("Password123!"),
        phone="555-0100",
        address="Test City",
        country="Testland",
        education="QA",
        experience="Testing",
        skills="Testing",
        resume_path="",
        is_verified=True,
        age_verified=True,
        legally_eligible=True,
    )
    company = Company(
        company_name="Codex QA Co",
        email=co_email,
        password_hash=generate_password_hash("Password123!"),
        is_verified=True,
    )
    db.session.add_all([seeker, company])
    db.session.commit()
    job = JobListing(
        company_id=company.id,
        title="QA Flow Tester",
        description="Test job",
        required_skills="Testing",
        location="Remote",
        job_type="Full-time",
        job_location_type="Remote",
        experience_level="Entry Level",
    )
    db.session.add(job)
    db.session.commit()

    try:
        client = app.test_client()
        login = client.post(
            "/login/seeker",
            data={"email": email, "password": "Password123!"},
            follow_redirects=False,
        )
        dashboard = client.get("/dashboard/seeker")
        invalid_swipe = client.post("/swipe", json={"job_id": job.id, "direction": "up"})
        application = client.post("/swipe", json={"job_id": job.id, "direction": "right"})
        duplicate = client.post("/swipe", json={"job_id": job.id, "direction": "right"})
        apply_route = client.get(f"/job/{job.id}/apply", follow_redirects=False)
        application_count = JobSwipe.query.filter_by(
            seeker_id=seeker.id,
            job_id=job.id,
            direction="right",
        ).count()
        notification_count = Notification.query.filter_by(
            user_id=company.id,
            user_type="company",
        ).count()
        print({
            "login_status": login.status_code,
            "login_location": login.location,
            "dashboard_status": dashboard.status_code,
            "invalid_swipe_status": invalid_swipe.status_code,
            "application_status": application.status_code,
            "application_json": application.json,
            "duplicate_json": duplicate.json,
            "apply_route_location": apply_route.location,
            "applications": application_count,
            "notifications": notification_count,
        })
    finally:
        Notification.query.filter_by(user_id=company.id, user_type="company").delete()
        JobSwipe.query.filter_by(seeker_id=seeker.id).delete()
        db.session.delete(job)
        db.session.delete(seeker)
        db.session.delete(company)
        db.session.commit()
