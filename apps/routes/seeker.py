"""
app/routes/seeker.py – Seeker-facing routes.
Covers: dashboard (with filters & AI scoring), profile edit, swipe action.
"""

import os
import uuid
from datetime import datetime

from flask import (
    Blueprint, render_template, request, redirect,
    url_for, session, flash, jsonify,
)
from werkzeug.utils import secure_filename

from ..extensions import db
from ..models import Seeker, JobListing, JobSwipe, SavedJob, RecentlyViewedJob, UploadedResume, RecommendationHistory
from ..services.email_service import send_application_emails
from ..services.notification_service import create_notification
from utils.helpers import allowed_file
from utils.applicant_presenter import existing_static_path
from utils.tfidf import parse_resume, match_resume_to_job, extract_keywords, filter_jobs_by_preferences, extract_skills, recommend_jobs_for_resume
from utils.resume_parser import process_resume
from utils.ats import calculate_ats_score

seeker_bp = Blueprint('seeker', __name__)

ALLOWED_RESUME = {'pdf', 'doc', 'docx'}

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



def _require_seeker():
    """Return the logged-in Seeker or None (also clears invalid session)."""
    seeker_id = session.get('seeker_id')
    if not seeker_id:
        return None
    seeker = db.session.get(Seeker, seeker_id)
    if not seeker:
        session.clear()
    return seeker


def apply_to_job(seeker, job):
    """Create a right-swipe application and send side effects once."""
    existing = JobSwipe.query.filter_by(seeker_id=seeker.id, job_id=job.id).first()
    if existing:
        return existing, False

    resume_text = parse_resume(seeker.resume_path) if seeker.resume_path and os.path.exists(seeker.resume_path) else ""
    job_full_text = f"{job.title} {job.description} {job.required_skills}"
    match_score = match_resume_to_job(resume_text, job_full_text) if resume_text else 0
    ats_score = calculate_ats_score(resume_text, job_full_text).get("score", 0) if resume_text else 0

    application = JobSwipe(
        seeker_id=seeker.id,
        job_id=job.id,
        direction="right",
        status="pending",
        match_score=float(match_score),
        ats_score=float(ats_score),
        ai_rank_score=float(match_score * 0.7 + ats_score * 0.3),
    )
    db.session.add(application)
    db.session.commit()

    if job.company:
        send_application_emails(
            seeker.email,
            f"{seeker.first_name} {seeker.last_name}",
            job.company.email,
            job.company.company_name,
            job.title,
            seeker.resume_path,
        )
        create_notification(
            user_id=job.company_id,
            user_type="company",
            message=f"New applicant: {seeker.first_name} {seeker.last_name} for '{job.title}'",
            type="application",
        )

    return application, True


# ── Seeker Dashboard ──────────────────────────────────────────────────────────
@seeker_bp.route('/dashboard/seeker')
def seeker_dashboard():
    seeker = _require_seeker()
    if not seeker:
        return redirect(url_for('auth.login_seeker'))

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
            "logo_path":        existing_static_path(job.company.logo_path),
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


# ── Swipe (JSON endpoint) ─────────────────────────────────────────────────────
@seeker_bp.route('/swipe', methods=['POST'])
def swipe():
    if 'seeker_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    data      = request.get_json(silent=True) or {}
    job_id    = data.get("job_id")
    direction = data.get("direction")

    if not job_id or direction not in ('left', 'right'):
        return jsonify({'error': 'Invalid data'}), 400

    # Duplicate-swipe guard
    if JobSwipe.query.filter_by(seeker_id=session['seeker_id'], job_id=job_id).first():
        return jsonify({'status': 'already_swiped'})

    seeker = db.session.get(Seeker, session['seeker_id'])
    job    = db.session.get(JobListing, job_id)
    if not seeker or not job:
        return jsonify({'error': 'Not found'}), 404

    if direction == 'right':
        application, created = apply_to_job(seeker, job)
        return jsonify({
            "status": "ok" if created else "already_swiped",
            "direction": "right",
            "match_score": application.match_score or 0,
        })

    new_swipe = JobSwipe(
        seeker_id=session['seeker_id'],
        job_id=job_id,
        direction="left",
        status="pending",
        match_score=0,
        ats_score=0,
        ai_rank_score=0,
    )
    db.session.add(new_swipe)
    db.session.commit()

    return jsonify({'status': 'ok', 'direction': 'left', 'match_score': 0})


# ── Edit Seeker Profile ───────────────────────────────────────────────────────
@seeker_bp.route('/profile/seeker', methods=['GET', 'POST'])
def edit_seeker_profile():
    from flask import current_app
    from datetime import datetime

    seeker = _require_seeker()
    if not seeker:
        return redirect(url_for('auth.login_seeker'))

    if request.method == 'POST':
        resume_path = request.form.get('existing_resume', '')
        resume_file = request.files.get('resume')
        resume_updated = False
        if resume_file and resume_file.filename and allowed_file(resume_file.filename, ALLOWED_RESUME):
            fname       = secure_filename(f'{uuid.uuid4()}_{resume_file.filename}')
            resume_path = os.path.join(current_app.config['RESUME_FOLDER'], fname)
            resume_file.save(resume_path)
            converted = process_resume(resume_path, current_app.config['RESUME_FOLDER'])
            if converted:
                resume_path = converted.get('resume_path', resume_path)
            resume_updated = True

        seeker.first_name  = request.form['first_name']
        seeker.last_name   = request.form['last_name']
        seeker.phone       = request.form.get('phone', '')
        seeker.education   = request.form.get('education', '')
        seeker.experience  = request.form.get('experience', '')
        seeker.skills      = request.form.get('skills', '')
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

        flash('Profile updated!', 'success')
        return redirect(url_for('seeker.seeker_dashboard'))

    return render_template('edit_seeker_profile.html', seeker=seeker)


# ── API Recommendations (New) ───────────────────────────────────────────────
@seeker_bp.route('/api/recommendations')
def api_recommendations():
    if 'seeker_id' not in session:
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


# ── Save Job (New) ──────────────────────────────────────────────────────────
@seeker_bp.route('/api/jobs/<int:job_id>/save', methods=['POST'])
def save_job(job_id):
    if 'seeker_id' not in session:
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


# ── Recommendation History (New) ────────────────────────────────────────────
@seeker_bp.route('/api/recommendation-history')
def recommendation_history():
    if 'seeker_id' not in session:
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


# ── Apply Job (Redirect endpoint) (New) ─────────────────────────────────────
@seeker_bp.route('/job/<int:job_id>/apply')
def apply_job(job_id):
    if 'seeker_id' not in session:
        return redirect(url_for('auth.login_seeker'))

    seeker = db.session.get(Seeker, session["seeker_id"])
    job = db.session.get(JobListing, job_id)
    if not seeker:
        session.clear()
        return redirect(url_for('auth.login_seeker'))
    if not job:
        flash("Job not found.", "error")
        return redirect(url_for('seeker.seeker_dashboard'))

    _, created = apply_to_job(seeker, job)
    flash(
        "Application sent successfully!" if created else "You have already applied to this job.",
        "success" if created else "info",
    )
    return redirect(url_for('seeker.seeker_dashboard'))

