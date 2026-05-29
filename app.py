import os, sys
from dotenv import load_dotenv

load_dotenv()
import uuid
from datetime import datetime

from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify, send_from_directory
from utils.mail_helper import Message
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from werkzeug.exceptions import HTTPException

from config import Config
from extensions import db, migrate, mail
from models import (
    Seeker, Company, JobListing, JobSwipe, Notification,
    UploadedResume, RecommendationHistory, SavedJob, RecentlyViewedJob
)
from apps.services import NotificationService, EligibilityService
from apps.models import EligibilityQuestion
from utils.tfidf import (
    parse_resume, match_resume_to_job, extract_keywords, extract_skills,
    recommend_jobs_for_resume
)
from utils.ats import calculate_ats_score
from utils.resume_parser import process_resume

app = Flask(__name__, static_folder=None)
app.config.from_object(Config)


@app.route("/static/<path:filename>", endpoint="static")
def static_files(filename):
    """Serve existing asset folders without changing frontend paths or CSS."""
    normalized = filename.replace("\\", "/")
    static_root = os.path.join(app.root_path, "static")
    static_path = os.path.abspath(os.path.join(static_root, normalized))
    if static_path.startswith(os.path.abspath(static_root)) and os.path.exists(static_path):
        return send_from_directory(static_root, normalized)

    safe_roots = {
        "css/": os.path.join(app.root_path, "css"),
        "js/": os.path.join(app.root_path, "js"),
        "uploads/": os.path.join(app.root_path, "uploads"),
    }
    for prefix, directory in safe_roots.items():
        if normalized.startswith(prefix):
            return send_from_directory(directory, normalized[len(prefix):])
    return send_from_directory(static_root, normalized)

# Initialize extensions
db.init_app(app)
migrate.init_app(app, db)
mail.init_app(app)

# Ensure tables are created (especially for local SQLite)
with app.app_context():
    try:
        db.create_all()
        # Initialize default eligibility questions
        EligibilityService.create_eligibility_questions()
    except Exception as e:
        print(f"Note: Database creation skipped or failed: {e}")

# Register Blueprints
from apps.routes.notifications import notifications_bp
from apps.routes.eligibility import eligibility_bp

app.register_blueprint(notifications_bp, url_prefix='')
app.register_blueprint(eligibility_bp, url_prefix='')


# ── Error Handlers ────────────────────────────────────────────────────────────
@app.errorhandler(Exception)
def handle_exception(e):
    if isinstance(e, HTTPException):
        return e
    import traceback
    traceback.print_exc()
    return render_template("error.html", error=str(e)), 500

@app.errorhandler(404)
def not_found(e):
    return render_template("error.html", error="Page not found (404)"), 404


os.makedirs(app.config["RESUME_FOLDER"], exist_ok=True)
os.makedirs(app.config["LOGO_FOLDER"], exist_ok=True)

ALLOWED_RESUME = {"pdf", "doc", "docx"}
ALLOWED_LOGO   = {"png", "jpg", "jpeg", "webp"}


def allowed_file(filename, allowed):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in allowed


# ── Email Helpers ─────────────────────────────────────────────────────────────
def send_application_emails(seeker_email, seeker_name, company_email, company_name, job_title, resume_path):
    """Send application notification emails to both company and seeker."""
    # To Company
    msg1 = Message(f"New applicant for {job_title}", recipients=[company_email])
    msg1.html = f"""
    <div style="font-family:sans-serif;max-width:520px;margin:auto;background:#0f172a;padding:2rem;border-radius:16px;color:#fff">
      <h2 style="color:#3b82f6;margin-bottom:0.5rem">CareerSwipe</h2>
      <p style="color:#94a3b8;margin-bottom:1.5rem">New Application Received</p>
      <p><b style="color:#fff">{seeker_name}</b> <span style="color:#94a3b8">has applied for</span> <b style="color:#3b82f6">{job_title}</b></p>
      <p style="color:#94a3b8;margin-top:1rem">Resume is attached to this email.</p>
      <div style="margin-top:2rem;padding-top:1rem;border-top:1px solid rgba(255,255,255,0.1);font-size:12px;color:#64748b">
        CareerSwipe · Smart Job Matching
      </div>
    </div>"""
    if resume_path and os.path.exists(resume_path):
        with open(resume_path, "rb") as fp:
            msg1.attach(os.path.basename(resume_path), "application/octet-stream", fp.read())
    try:
        mail.send(msg1)
    except Exception:
        pass

    # To Seeker
    msg2 = Message(f"Application sent to {company_name}", recipients=[seeker_email])
    msg2.html = f"""
    <div style="font-family:sans-serif;max-width:520px;margin:auto;background:#0f172a;padding:2rem;border-radius:16px;color:#fff">
      <h2 style="color:#3b82f6">CareerSwipe</h2>
      <p style="color:#94a3b8">Application Confirmation</p>
      <p>Your application for <b style="color:#3b82f6">{job_title}</b> at <b style="color:#fff">{company_name}</b> was sent successfully! ✅</p>
    </div>"""
    try:
        mail.send(msg2)
    except Exception:
        pass


def create_notification(user_id, user_type, message, type='system'):
    """Helper to create a notification record."""
    try:
        new_notif = Notification(
            user_id=user_id,
            user_type=user_type,
            message=message,
            type=type
        )
        db.session.add(new_notif)
        db.session.commit()
        return True
    except Exception as e:
        print(f"Error creating notification: {e}")
        db.session.rollback()
        return False


# ════════════════════════════════════════════════════════════════════════════
#  AUTH ROUTES
# ════════════════════════════════════════════════════════════════════════════
def store_uploaded_resume(seeker_id, resume_path, extracted_text="", extracted_skills=None):
    """Persist parsed resume content and mark older resumes inactive."""
    if not seeker_id or not resume_path:
        return None

    try:
        UploadedResume.query.filter_by(seeker_id=seeker_id, is_active=True).update({"is_active": False})
        resume = UploadedResume(
            seeker_id=seeker_id,
            filename=os.path.basename(resume_path),
            file_path=resume_path,
            extracted_text=extracted_text or "",
            extracted_skills=", ".join(extracted_skills or []),
            is_active=True,
        )
        db.session.add(resume)
        db.session.commit()
        return resume
    except Exception as e:
        print(f"Error storing resume: {e}")
        db.session.rollback()
        return None


def get_active_resume(seeker):
    """Return the active stored resume, creating one from the current path if needed."""
    active_resume = UploadedResume.query.filter_by(
        seeker_id=seeker.id,
        is_active=True
    ).order_by(UploadedResume.created_at.desc()).first()

    if active_resume:
        return active_resume

    if seeker.resume_path and os.path.exists(seeker.resume_path):
        resume_text = parse_resume(seeker.resume_path)
        skills = extract_skills(" ".join([resume_text, seeker.skills or "", seeker.education or ""]))
        return store_uploaded_resume(seeker.id, seeker.resume_path, resume_text, skills)

    return None


def save_recommendation_history(seeker_id, resume_id, recommendations):
    """Store the latest recommendation scores for history and analytics."""
    if not seeker_id:
        return

    try:
        for item in recommendations[:25]:
            job = item["job"]
            db.session.add(RecommendationHistory(
                seeker_id=seeker_id,
                job_id=job.id,
                resume_id=resume_id,
                similarity_score=item["similarity_score"],
                match_percentage=item["match_percentage"],
                matched_skills=", ".join(item["matched_skills"]),
                missing_skills=", ".join(item["missing_skills"]),
                recommended_skills=", ".join(item["recommended_skills"]),
            ))
        db.session.commit()
    except Exception as e:
        print(f"Error storing recommendations: {e}")
        db.session.rollback()


def is_relevant_recommendation(seeker, item):
    """Keep only jobs with a meaningful resume/profile signal."""
    job = item["job"]
    seeker_terms = " ".join([
        seeker.skills or "",
        seeker.education or "",
        seeker.experience or "",
        seeker.career_field or "",
        seeker.desired_roles or "",
    ]).lower()
    job_title = (job.title or "").lower()
    desired_roles = [
        role.strip().lower()
        for role in (seeker.desired_roles or "").replace("|", ",").split(",")
        if role.strip()
    ]
    seeker_skill_tokens = {
        skill.strip().lower()
        for skill in (seeker.skills or "").replace("|", ",").split(",")
        if skill.strip()
    }
    profile_tokens = {
        term for term in seeker_terms.replace(",", " ").split()
        if len(term) > 2
    }
    career_title_terms = {
        "it / software": {"it", "software", "developer", "engineer", "programmer", "data", "analyst", "python", "java"},
        "business / management": {"business", "manager", "management", "operations", "analyst", "coordinator"},
        "finance / accounting": {"finance", "accountant", "accounting", "audit", "bank", "tax"},
        "healthcare / medical": {"healthcare", "medical", "nurse", "doctor", "care", "clinic"},
        "engineering": {"engineer", "engineering", "mechanical", "civil", "electrical"},
        "education / teaching": {"teacher", "teaching", "tutor", "lecturer", "education"},
        "marketing / sales": {"marketing", "sales", "seo", "brand", "content"},
        "design / creative": {"design", "designer", "ui", "ux", "creative", "graphic"},
        "hospitality / tourism": {"hospitality", "hotel", "tourism", "travel", "guest"},
    }
    career_terms = career_title_terms.get((seeker.career_field or "").lower(), set())

    title_matches_role = any(role in job_title or job_title in role for role in desired_roles)
    title_matches_skill = any(skill in job_title for skill in seeker_skill_tokens)
    title_matches_profile = any(term in job_title for term in profile_tokens)
    title_matches_career = any(term in job_title for term in career_terms)

    return (
        item["match_percentage"] >= 12
        and (title_matches_role or title_matches_skill or title_matches_profile or title_matches_career)
    )


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/upload-resume", methods=["GET", "POST"])
def upload_resume_step():
    if request.method == "POST":
        resume_file = request.files.get("resume")
        if resume_file and resume_file.filename and allowed_file(resume_file.filename, ALLOWED_RESUME):
            fname = secure_filename(f"{uuid.uuid4()}_{resume_file.filename}")
            resume_path = os.path.join(app.config["RESUME_FOLDER"], fname)
            resume_file.save(resume_path)
            
            # Process resume for extraction
            extracted_data = process_resume(resume_path, app.config["RESUME_FOLDER"])
            
            if extracted_data:
                # User wants session["resume_data"] with "name", "email", "skills", "resume_path"
                extracted_name = f"{extracted_data.get('first_name', '')} {extracted_data.get('last_name', '')}".strip()
                extracted_email = extracted_data.get("email", "")
                extracted_skills = extracted_data.get("skills", "")
                
                # Debugging Step
                print(f"DEBUG: Extracted for session: {extracted_name}, {extracted_email}", flush=True)
                
                # Store all extracted fields in session for registration form
                session["resume_data"] = {
                    "name": extracted_name,
                    "first_name": extracted_data.get("first_name", ""),
                    "last_name": extracted_data.get("last_name", ""),
                    "email": extracted_email,
                    "phone": extracted_data.get("phone", ""),
                    "address": extracted_data.get("address", ""),
                    "country": extracted_data.get("country", ""),
                    "gender": extracted_data.get("gender", "Other"),
                    "dob": extracted_data.get("dob", ""),
                    "education": extracted_data.get("education", ""),
                    "experience": extracted_data.get("experience", ""),
                    "experience_type": extracted_data.get("experience_type", "Full-time"),
                    "career_field": extracted_data.get("career_field", "Other"),
                    "job_location_type": extracted_data.get("job_location_type", "Local"),
                    "desired_roles": extracted_data.get("desired_roles", ""),
                    "employment_type": extracted_data.get("employment_type", "Full-time"),
                    "salary": extracted_data.get("salary", ""),
                    "availability": extracted_data.get("availability", "Immediate"),
                    "skills": extracted_skills,
                    "resume_path": resume_path
                }
                session.modified = True 
                flash("Resume analyzed! Please verify your information.", "success")
            else:
                flash("We couldn't extract all details from your resume, but you can still apply manually.", "warning")
                session["resume_data"] = {"resume_path": resume_path}
                session.modified = True
            
            return redirect(url_for("register_seeker"))
        else:
            flash("Invalid file type. Please upload a PDF, DOC, or DOCX.", "error")
            return redirect(url_for("upload_resume_step"))
            
    return render_template("upload_resume.html")


@app.route("/register/seeker", methods=["GET", "POST"])
def register_seeker():
    resume_data = session.get("resume_data", {})
    # Debugging Step
    print(f"DEBUG: Session data in register_seeker: {resume_data}", flush=True)
    
    eligibility_questions = EligibilityQuestion.query.filter_by(
        is_active=True
    ).order_by(EligibilityQuestion.display_order).all()

    if request.method == "POST":
        email = request.form["email"].strip().lower()

        if Seeker.query.filter_by(email=email).first():
            flash("Email already registered.", "error")
            return redirect(url_for("register_seeker"))

        # Verify eligibility and age
        age_verified = request.form.get("age_verified") == "on"
        legally_eligible = request.form.get("legally_eligible") == "on"
        
        if not age_verified or not legally_eligible:
            flash("You must confirm you are 18+ and eligible to work.", "error")
            return redirect(url_for("register_seeker"))

        missing_answers = []
        for question in eligibility_questions:
            field_name = f"question_{question.id}"
            value = request.form.get(field_name)
            if question.is_mandatory:
                if question.field_type == "checkbox":
                    if not value:
                        missing_answers.append(question.question_text)
                elif not value or str(value).strip() == "":
                    missing_answers.append(question.question_text)

        if missing_answers:
            flash(
                "Please answer the required eligibility questions: " + ", ".join(missing_answers),
                "error"
            )
            return redirect(url_for("register_seeker"))

        resume_path = resume_data.get("resume_path", "")
        
        resume_file = request.files.get("resume")
        if resume_file and resume_file.filename and allowed_file(resume_file.filename, ALLOWED_RESUME):
            fname = secure_filename(f"{uuid.uuid4()}_{resume_file.filename}")
            resume_path = os.path.join(app.config["RESUME_FOLDER"], fname)
            resume_file.save(resume_path)

        new_seeker = Seeker(
            first_name=request.form["first_name"],
            last_name=request.form["last_name"],
            email=email,
            password_hash=generate_password_hash(request.form["password"]),
            phone=request.form.get("phone", ""),
            address=request.form.get("address", ""),
            country=request.form.get("country", ""),
            education=request.form.get("education", ""),
            experience=request.form.get("experience", ""),
            skills=request.form.get("skills", ""),
            resume_path=resume_path,
            gender=request.form.get("gender"),
            dob=request.form.get("dob"),
            experience_type=request.form.get("experience_type"),
            career_field=request.form.get("career_field"),
            job_status=request.form.get("job_status", "Searching"),
            job_location_type=request.form.get("job_location_type"),
            desired_roles=request.form.get("desired_roles"),
            salary_expectation=request.form.get("salary"),
            availability=request.form.get("availability"),
            is_verified=True,
            age_verified=age_verified,
            legally_eligible=legally_eligible
        )
        db.session.add(new_seeker)
        db.session.commit()

        if resume_path and os.path.exists(resume_path):
            resume_text = parse_resume(resume_path)
            resume_skills = extract_skills(" ".join([
                resume_text,
                request.form.get("skills", ""),
                request.form.get("education", ""),
                request.form.get("experience", ""),
            ]))
            store_uploaded_resume(new_seeker.id, resume_path, resume_text, resume_skills)

        session.pop("resume_data", None)

        flash("Account created! You can log in now.", "success")
        return redirect(url_for("login_seeker"))
        
    return render_template("register_seeker.html", 
                           name=resume_data.get("name"),
                           first_name=resume_data.get("first_name"),
                           last_name=resume_data.get("last_name"),
                           email=resume_data.get("email"),
                           phone=resume_data.get("phone"),
                           address=resume_data.get("address"),
                           gender=resume_data.get("gender"),
                           dob=resume_data.get("dob"),
                           education=resume_data.get("education"),
                           experience=resume_data.get("experience"),
                           experience_type=resume_data.get("experience_type"),
                           career_field=resume_data.get("career_field"),
                           job_location_type=resume_data.get("job_location_type"),
                           desired_roles=resume_data.get("desired_roles"),
                           employment_type=resume_data.get("employment_type"),
                           salary=resume_data.get("salary"),
                           availability=resume_data.get("availability"),
                           skills=resume_data.get("skills"),
                           resume_path=resume_data.get("resume_path"),
                           eligibility_questions=[q.to_dict() for q in eligibility_questions])


@app.route("/register/company", methods=["GET", "POST"])
def register_company():
    if request.method == "POST":
        email = request.form["email"].strip().lower()

        if Company.query.filter_by(email=email).first():
            flash("Email already registered.", "error")
            return redirect(url_for("register_company"))

        logo_file = request.files.get("logo")
        logo_path = ""
        if logo_file and logo_file.filename and allowed_file(logo_file.filename, ALLOWED_LOGO):
            fname = secure_filename(f"{uuid.uuid4()}_{logo_file.filename}")
            logo_path = os.path.join(app.config["LOGO_FOLDER"], fname)
            logo_file.save(logo_path)
        else:
            flash("Please upload a valid company logo.", "error")
            return redirect(url_for("register_company"))

        new_company = Company(
            company_name=request.form["company_name"],
            email=email,
            password_hash=generate_password_hash(request.form["password"]),
            description=request.form.get("description", ""),
            industry=request.form.get("industry", ""),
            website=request.form.get("website", ""),
            country=request.form.get("country", ""),
            logo_path=logo_path,
            is_verified=True,
            age_verified=request.form.get("age_verified") == "on",
            legally_eligible=request.form.get("legally_eligible") == "on"
        )
        db.session.add(new_company)
        db.session.commit()

        flash("Company registered!", "success")
        return redirect(url_for("login_company"))

    return render_template("register_company.html")


@app.route("/login/seeker", methods=["GET", "POST"])
def login_seeker():
    if request.method == "POST":
        email = request.form["email"].strip().lower()
        user = Seeker.query.filter_by(email=email).first()

        if user and check_password_hash(user.password_hash, request.form["password"]):
            session["seeker_id"] = user.id
            session["seeker_name"] = user.first_name
            return redirect(url_for("seeker_dashboard"))
        flash("Invalid email or password.", "error")
    return render_template("login_seeker.html")


@app.route("/login/company", methods=["GET", "POST"])
def login_company():
    if request.method == "POST":
        email = request.form["email"].strip().lower()
        co = Company.query.filter_by(email=email).first()

        if co and check_password_hash(co.password_hash, request.form["password"]):
            session["company_id"] = co.id
            session["company_name"] = co.company_name
            return redirect(url_for("company_dashboard"))
        flash("Invalid email or password.", "error")
    return render_template("login_company.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))


# ════════════════════════════════════════════════════════════════════════════
#  SEEKER FEATURES
# ════════════════════════════════════════════════════════════════════════════
@app.route("/dashboard/seeker")
def seeker_dashboard():
    if "seeker_id" not in session:
        return redirect(url_for("login_seeker"))

    seeker = db.session.get(Seeker, session["seeker_id"])
    if not seeker:
        session.clear()
        return redirect(url_for("login_seeker"))

    swiped_job_ids = [swipe.job_id for swipe in seeker.swipes]

    # ── Indeed-style Filters ──
    job_type          = request.args.get("job_type")
    exp_level         = request.args.get("experience_level")
    location_type     = request.args.get("location_type")
    location          = request.args.get("location")
    min_sal           = request.args.get("min_salary", type=int)
    min_skill_match   = request.args.get("min_skill_match", type=int)
    min_matched_skills = request.args.get("min_matched_skills", type=int)

    query = JobListing.query
    if swiped_job_ids:
        query = query.filter(~JobListing.id.in_(swiped_job_ids))
    if job_type:
        query = query.filter(JobListing.job_type == job_type)
    if exp_level:
        query = query.filter(JobListing.experience_level == exp_level)
    if location_type:
        query = query.filter(JobListing.job_location_type == location_type)
    if location:
        query = query.filter(JobListing.location.ilike(f"%{location}%"))
    if min_sal:
        query = query.filter(JobListing.max_salary >= min_sal)

    available_jobs_data = (
        query.order_by(JobListing.is_boosted.desc(), JobListing.created_at.desc())
        .limit(50)
        .all()
    )

    active_resume = get_active_resume(seeker)
    resume_text = active_resume.extracted_text if active_resume else ""
    if not resume_text and seeker.resume_path and os.path.exists(seeker.resume_path):
        resume_text = parse_resume(seeker.resume_path)

    keywords = extract_keywords(" ".join([resume_text, seeker.skills or ""])) if resume_text or seeker.skills else []
    recommendations = recommend_jobs_for_resume(seeker, resume_text, available_jobs_data)
    recommendations = [
        item for item in recommendations
        if is_relevant_recommendation(seeker, item)
    ]
    if min_skill_match is not None:
        recommendations = [
            item for item in recommendations
            if item["skill_match_percentage"] >= min_skill_match
        ]
    if min_matched_skills is not None:
        recommendations = [
            item for item in recommendations
            if len(item["matched_skills"]) >= min_matched_skills
        ]
    if recommendations:
        save_recommendation_history(seeker.id, active_resume.id if active_resume else None, recommendations)

    saved_job_ids = {
        saved.job_id for saved in SavedJob.query.filter_by(seeker_id=seeker.id).all()
    }

    jobs = []
    for item in recommendations:
        job = item["job"]
        job_desc_full = f"{job.title} {job.description} {job.required_skills} {job.tags or ''}"
        ats_data = calculate_ats_score(resume_text, job_desc_full) if resume_text else {}

        jobs.append({
            "id":               job.id,
            "title":            job.title,
            "company_name":     job.company.company_name,
            "logo_path":        job.company.logo_path,
            "location":         job.location,
            "job_type":         job.job_type,
            "job_location_type": job.job_location_type,
            "experience_level": job.experience_level,
            "salary":           job.salary,
            "max_salary":       job.max_salary,
            "is_boosted":       job.is_boosted,
            "description":      job.description,
            "required_skills":  job.required_skills,
            "match_score":      item["match_percentage"],
            "similarity_score": item["similarity_score"],
            "matched_skills":   item["matched_skills"],
            "matched_skills_count": len(item["matched_skills"]),
            "missing_skills":   item["missing_skills"],
            "recommended_skills": item["recommended_skills"],
            "skill_match_percentage": item["skill_match_percentage"],
            "skill_match": item["skill_match_percentage"],
            "location_match": 100 if seeker.job_location_type and job.job_location_type and seeker.job_location_type.lower() in job.job_location_type.lower() else 0,
            "relevance_score": item["match_percentage"],
            "is_best_match":    item["is_best_match"],
            "is_saved":         job.id in saved_job_ids,
            "ats_score":        ats_data.get("score", 0) if ats_data else 0,
            "ats_findings":     ats_data.get("findings", []) if ats_data else [],
        })

    for job in jobs[:5]:
        viewed = RecentlyViewedJob.query.filter_by(seeker_id=seeker.id, job_id=job["id"]).first()
        if viewed:
            viewed.viewed_at = datetime.utcnow()
        else:
            db.session.add(RecentlyViewedJob(seeker_id=seeker.id, job_id=job["id"]))
    if jobs:
        db.session.commit()

    # Fetch applied jobs
    swipes = (
        JobSwipe.query
        .filter_by(seeker_id=session["seeker_id"], direction="right")
        .order_by(JobSwipe.created_at.desc())
        .all()
    )
    applications = [
        {
            "title":        s.job_listing.title,
            "company_name": s.job_listing.company.company_name,
            "applied_at":   s.created_at,
            "status":       s.status,
        }
        for s in swipes
    ]

    saved_jobs = (
        SavedJob.query
        .filter_by(seeker_id=seeker.id)
        .order_by(SavedJob.created_at.desc())
        .limit(10)
        .all()
    )
    recently_viewed = (
        RecentlyViewedJob.query
        .filter_by(seeker_id=seeker.id)
        .order_by(RecentlyViewedJob.viewed_at.desc())
        .limit(10)
        .all()
    )
    recommendation_history_rows = (
        RecommendationHistory.query
        .filter_by(seeker_id=seeker.id)
        .order_by(RecommendationHistory.created_at.desc())
        .limit(10)
        .all()
    )

    return render_template(
        "seeker_dashboard.html",
        seeker=seeker,
        jobs=jobs,
        applications=applications,
        keywords=keywords,
        saved_jobs=saved_jobs,
        recently_viewed=recently_viewed,
        recommendation_history=recommendation_history_rows,
    )


@app.route("/api/recommendations")
def api_recommendations():
    if "seeker_id" not in session:
        return jsonify({"error": "Unauthorized"}), 401

    seeker = db.session.get(Seeker, session["seeker_id"])
    if not seeker:
        return jsonify({"error": "Not found"}), 404

    active_resume = get_active_resume(seeker)
    resume_text = active_resume.extracted_text if active_resume else ""
    jobs = JobListing.query.order_by(JobListing.created_at.desc()).limit(100).all()
    recommendations = recommend_jobs_for_resume(seeker, resume_text, jobs, limit=25)
    recommendations = [
        item for item in recommendations
        if is_relevant_recommendation(seeker, item)
    ]
    save_recommendation_history(seeker.id, active_resume.id if active_resume else None, recommendations)

    return jsonify([{
        "job_id": item["job"].id,
        "title": item["job"].title,
        "company_name": item["job"].company.company_name,
        "location": item["job"].location,
        "match_percentage": item["match_percentage"],
        "required_skills": item["job"].required_skills,
        "matched_skills": item["matched_skills"],
        "missing_skills": item["missing_skills"],
        "recommended_skills": item["recommended_skills"],
        "is_best_match": item["is_best_match"],
    } for item in recommendations])


@app.route("/api/jobs/<int:job_id>/save", methods=["POST"])
def save_job(job_id):
    if "seeker_id" not in session:
        return jsonify({"error": "Unauthorized"}), 401

    if not db.session.get(JobListing, job_id):
        return jsonify({"error": "Job not found"}), 404

    existing = SavedJob.query.filter_by(seeker_id=session["seeker_id"], job_id=job_id).first()
    if existing:
        db.session.delete(existing)
        db.session.commit()
        return jsonify({"status": "removed", "saved": False})

    db.session.add(SavedJob(seeker_id=session["seeker_id"], job_id=job_id))
    db.session.commit()
    return jsonify({"status": "saved", "saved": True})


@app.route("/api/recommendation-history")
def recommendation_history():
    if "seeker_id" not in session:
        return jsonify({"error": "Unauthorized"}), 401

    rows = (
        RecommendationHistory.query
        .filter_by(seeker_id=session["seeker_id"])
        .order_by(RecommendationHistory.created_at.desc())
        .limit(25)
        .all()
    )
    return jsonify([{
        "job_id": row.job_id,
        "title": row.job_listing.title,
        "company_name": row.job_listing.company.company_name,
        "match_percentage": row.match_percentage,
        "similarity_score": row.similarity_score,
        "matched_skills": row.matched_skills,
        "missing_skills": row.missing_skills,
        "recommended_skills": row.recommended_skills,
        "created_at": row.created_at.strftime("%Y-%m-%d %H:%M:%S"),
    } for row in rows])


@app.route("/swipe", methods=["POST"])
def swipe():
    if "seeker_id" not in session:
        return jsonify({"error": "Unauthorized"}), 401

    data      = request.get_json()
    job_id    = data.get("job_id")
    direction = data.get("direction")

    if not job_id or direction not in ("left", "right"):
        return jsonify({"error": "Invalid data"}), 400

    # Duplicate check
    if JobSwipe.query.filter_by(seeker_id=session["seeker_id"], job_id=job_id).first():
        return jsonify({"status": "already_swiped"})

    seeker = db.session.get(Seeker, session["seeker_id"])
    job    = db.session.get(JobListing, job_id)

    if not seeker or not job:
        return jsonify({"error": "Not found"}), 404

    resume_text   = parse_resume(seeker.resume_path) if seeker.resume_path and os.path.exists(seeker.resume_path) else ""
    job_full_text = f"{job.title} {job.description} {job.required_skills}"
    m_score = match_resume_to_job(resume_text, job_full_text) if resume_text else 0
    a_score = calculate_ats_score(resume_text, job_full_text).get("score", 0) if resume_text else 0

    new_swipe = JobSwipe(
        seeker_id=session["seeker_id"],
        job_id=job_id,
        direction=direction,
        status="pending",
        match_score=float(m_score),
        ats_score=float(a_score),
        ai_rank_score=float(m_score * 0.7 + a_score * 0.3),
    )
    db.session.add(new_swipe)
    db.session.commit()

    if direction == "right" and job.company:
        send_application_emails(
            seeker.email,
            f"{seeker.first_name} {seeker.last_name}",
            job.company.email,
            job.company.company_name,
            job.title,
            seeker.resume_path,
        )
        # ✅ Trigger company notification
        create_notification(
            user_id=job.company_id,
            user_type='company',
            message=f"New applicant: {seeker.first_name} {seeker.last_name} for '{job.title}'",
            type='application'
        )

    return jsonify({"status": "ok", "direction": direction, "match_score": m_score})


@app.route("/profile/seeker", methods=["GET", "POST"])
def edit_seeker_profile():
    if "seeker_id" not in session:
        return redirect(url_for("login_seeker"))

    seeker = db.session.get(Seeker, session["seeker_id"])

    if request.method == "POST":
        resume_file = request.files.get("resume")
        resume_path = request.form.get("existing_resume", "")
        resume_updated = False
        if resume_file and resume_file.filename and allowed_file(resume_file.filename, ALLOWED_RESUME):
            fname = secure_filename(f"{uuid.uuid4()}_{resume_file.filename}")
            resume_path = os.path.join(app.config["RESUME_FOLDER"], fname)
            resume_file.save(resume_path)
            resume_updated = True

        seeker.first_name = request.form["first_name"]
        seeker.last_name  = request.form["last_name"]
        seeker.phone      = request.form.get("phone", "")
        seeker.education  = request.form.get("education", "")
        seeker.experience = request.form.get("experience", "")
        seeker.skills     = request.form.get("skills", "")
        seeker.resume_path = resume_path

        db.session.commit()

        if resume_updated and resume_path and os.path.exists(resume_path):
            resume_text = parse_resume(resume_path)
            resume_skills = extract_skills(" ".join([
                resume_text,
                seeker.skills or "",
                seeker.education or "",
                seeker.experience or "",
            ]))
            store_uploaded_resume(seeker.id, resume_path, resume_text, resume_skills)

        flash("Profile updated!", "success")
        return redirect(url_for("seeker_dashboard"))

    return render_template("edit_seeker_profile.html", seeker=seeker)


# ════════════════════════════════════════════════════════════════════════════
#  COMPANY FEATURES
# ════════════════════════════════════════════════════════════════════════════
@app.route("/dashboard/company")
def company_dashboard():
    if "company_id" not in session:
        return redirect(url_for("login_company"))

    company = db.session.get(Company, session["company_id"])
    if not company:
        session.clear()
        return redirect(url_for("login_company"))

    jobs = (
        JobListing.query
        .filter_by(company_id=session["company_id"])
        .order_by(JobListing.created_at.desc())
        .all()
    )

    swipes = (
        JobSwipe.query.join(JobListing)
        .filter(
            JobListing.company_id == session["company_id"],
            JobSwipe.direction == "right",
        )
        .order_by(JobSwipe.created_at.desc())
        .all()
    )

    applicants = [
        {
            "seeker_id":   sw.seeker.id,
            "first_name":  sw.seeker.first_name,
            "last_name":   sw.seeker.last_name,
            "email":       sw.seeker.email,
            "skills":      sw.seeker.skills,
            "resume_path": sw.seeker.resume_path,
            "job_title":   sw.job_listing.title,
            "applied_at":  sw.created_at,
            "status":      sw.status,
            "swipe_id":    sw.id,
            "match_score": sw.match_score,
            "ats_score":   sw.ats_score,
        }
        for sw in swipes
    ]

    return render_template(
        "company_dashboard.html",
        company=company,
        jobs=jobs,
        applicants=applicants,
    )


@app.route("/jobs/post", methods=["GET", "POST"])
def post_job():
    if "company_id" not in session:
        return redirect(url_for("login_company"))

    if request.method == "POST":
        new_job = JobListing(
            company_id=session["company_id"],
            title=request.form["title"],
            description=request.form["description"],
            required_skills=request.form.get("required_skills", ""),
            location=request.form.get("location", ""),
            job_type=request.form.get("job_type", "Full-time"),
            job_location_type=request.form.get("job_location_type", "Onsite"),
            experience_level=request.form.get("experience_level", "Entry Level"),
            min_experience=request.form.get("min_experience", 0, type=int),
            salary=request.form.get("salary", ""),
            max_salary=request.form.get("max_salary", 0, type=int),
            tags=request.form.get("tags", ""),
        )
        db.session.add(new_job)
        db.session.commit()
        flash("Job posted successfully!", "success")
        return redirect(url_for("company_dashboard"))

    return render_template("post_job.html")


@app.route("/applicant/<int:swipe_id>/<action>")
def update_applicant(swipe_id, action):
    if "company_id" not in session:
        return redirect(url_for("login_company"))

    swipe = db.session.get(JobSwipe, swipe_id)
    if not swipe:
        flash("Applicant not found.", "error")
        return redirect(url_for("company_dashboard"))

    if swipe.job_listing.company_id != session["company_id"]:
        flash("Unauthorized action.", "error")
        return redirect(url_for("company_dashboard"))

    action_map = {"shortlist": "shortlisted", "interview": "interview", "accept": "accepted", "reject": "rejected"}
    swipe.status = action_map.get(action, action + "ed")
    db.session.commit()

    seeker = swipe.seeker
    job    = swipe.job_listing
    action_text = action_map.get(action, action + "ed")

    msg = Message(f"Update on your application: {job.title}", recipients=[seeker.email])
    msg.html = f"""
    <div style="font-family:sans-serif;max-width:520px;margin:auto;background:#0f172a;padding:2rem;border-radius:16px;color:#fff">
      <h2 style="color:#3b82f6">CareerSwipe</h2>
      <p>Hi <b>{seeker.first_name}</b>,</p>
      <p>Your application for <b style="color:#3b82f6">{job.title}</b> at <b>{job.company.company_name}</b> has been <b style="color:#10b981">{action_text}</b>.</p>
      <p style="color:#94a3b8;margin-top:1rem">Login to your dashboard to see more details.</p>
    </div>"""
    try:
        mail.send(msg)
    except Exception:
        pass

    flash(f"Applicant {action_text}.", "success")

    # ✅ Trigger seeker notification
    notif_msg = f"Your application for {job.title} at {job.company.company_name} has been {action_text}."
    if action == "accept":
        notif_msg = f"Congratulations! 🎉 Your application for {job.title} at {job.company.company_name} has been ACCEPTED."
    elif action == "interview":
        notif_msg = f"Interview Scheduled! 📅 {job.company.company_name} wants to interview you for {job.title}."

    create_notification(
        user_id=seeker.id,
        user_type='seeker',
        message=notif_msg,
        type=action
    )

    return redirect(url_for("company_dashboard"))


# ── Notification Routes ───────────────────────────────────────────────────

@app.route("/notifications")
def notifications_history():
    user_id = session.get("seeker_id") or session.get("company_id")
    user_type = "seeker" if session.get("seeker_id") else "company"

    if not user_id:
        return redirect(url_for("index"))

    # Fetch all notifications for the user
    notifications = (
        Notification.query.filter_by(user_id=user_id, user_type=user_type)
        .order_by(Notification.created_at.desc())
        .all()
    )
    return render_template("notifications.html", notifications=notifications, user_type=user_type)


@app.route("/api/notifications")
def get_notifications():
    user_id = session.get("seeker_id") or session.get("company_id")
    user_type = "seeker" if session.get("seeker_id") else "company"

    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    limit = request.args.get("limit", 20, type=int)
    if limit < 1:
        limit = 20

    notifs = (
        Notification.query.filter_by(user_id=user_id, user_type=user_type)
        .order_by(Notification.created_at.desc())
        .limit(limit)
        .all()
    )

    return jsonify([{
        "id": n.id,
        "message": n.message,
        "type": n.type,
        "is_read": n.is_read,
        "created_at": n.created_at.strftime("%Y-%m-%d %H:%M:%S")
    } for n in notifs])


@app.route("/api/notifications/unread-count")
def get_unread_count():
    user_id = session.get("seeker_id") or session.get("company_id")
    user_type = "seeker" if session.get("seeker_id") else "company"

    if not user_id:
        return jsonify({"count": 0})

    count = Notification.query.filter_by(user_id=user_id, user_type=user_type, is_read=False).count()
    return jsonify({"count": count})


@app.route("/api/notifications/read/<int:notif_id>", methods=["POST"])
def mark_read(notif_id):
    user_id = session.get("seeker_id") or session.get("company_id")
    user_type = "seeker" if session.get("seeker_id") else "company"

    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    notif = Notification.query.get(notif_id)
    if notif and notif.user_id == user_id and notif.user_type == user_type:
        notif.is_read = True
        db.session.commit()
        return jsonify({"status": "ok"})

    return jsonify({"error": "Not found"}), 404


@app.route("/api/notifications/read-all", methods=["POST"])
def mark_all_read():
    user_id = session.get("seeker_id") or session.get("company_id")
    user_type = "seeker" if session.get("seeker_id") else "company"

    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    Notification.query.filter_by(user_id=user_id, user_type=user_type, is_read=False).update({"is_read": True})
    db.session.commit()
    return jsonify({"status": "ok"})


# ── Health Check ─────────────────────────────────────────────────────────────
@app.route("/api/health")
def health_check():
    return {"status": "healthy", "service": "CareerSwipe"}, 200


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=False, host="0.0.0.0", port=port)
