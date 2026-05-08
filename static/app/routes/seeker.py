"""
app/routes/seeker.py – Seeker-facing routes.
Covers: dashboard (with filters & AI scoring), profile edit, swipe action.
"""

import os
import uuid

from flask import (
    Blueprint, render_template, request, redirect,
    url_for, session, flash, jsonify,
)
from werkzeug.utils import secure_filename

from ..extensions import db
from ..models import Seeker, JobListing, JobSwipe
from ..services.email_service import send_application_emails
from ..services.notification_service import create_notification
from ..utils.helpers import allowed_file
from ..utils.tfidf import parse_resume, match_resume_to_job, extract_keywords
from ..utils.ats import calculate_ats_score

seeker_bp = Blueprint('seeker', __name__)

ALLOWED_RESUME = {'pdf', 'doc', 'docx'}


def _require_seeker():
    """Return the logged-in Seeker or None (also clears invalid session)."""
    seeker_id = session.get('seeker_id')
    if not seeker_id:
        return None
    seeker = db.session.get(Seeker, seeker_id)
    if not seeker:
        session.clear()
    return seeker


# ── Seeker Dashboard ──────────────────────────────────────────────────────────
@seeker_bp.route('/dashboard/seeker')
def seeker_dashboard():
    seeker = _require_seeker()
    if not seeker:
        return redirect(url_for('auth.login_seeker'))

    # IDs the seeker has already swiped on
    swiped_ids = [sw.job_id for sw in seeker.swipes]

    # ── Filters (Indeed-style) ────────────────────────────────────────────────
    job_type      = request.args.get('job_type')
    exp_level     = request.args.get('experience_level')
    location_type = request.args.get('location_type')
    location      = request.args.get('location')
    min_sal       = request.args.get('min_salary', type=int)

    query = JobListing.query
    if swiped_ids:
        query = query.filter(~JobListing.id.in_(swiped_ids))
    if job_type:
        query = query.filter(JobListing.job_type == job_type)
    if exp_level:
        query = query.filter(JobListing.experience_level == exp_level)
    if location_type:
        query = query.filter(JobListing.job_location_type == location_type)
    if location:
        query = query.filter(JobListing.location.ilike(f'%{location}%'))
    if min_sal:
        query = query.filter(JobListing.max_salary >= min_sal)

    raw_jobs = (
        query
        .order_by(JobListing.is_boosted.desc(), JobListing.created_at.desc())
        .limit(50)
        .all()
    )

    # ── AI scoring ────────────────────────────────────────────────────────────
    resume_text = ''
    if seeker.resume_path and os.path.exists(seeker.resume_path):
        resume_text = parse_resume(seeker.resume_path)
    keywords = extract_keywords(resume_text) if resume_text else []

    jobs = []
    for job in raw_jobs:
        full_text  = f'{job.title} {job.description} {job.required_skills} {job.tags or ""}'
        match      = match_resume_to_job(resume_text, full_text) if resume_text else 0
        ats_data   = calculate_ats_score(resume_text, full_text) if resume_text else {}

        jobs.append({
            'id':               job.id,
            'title':            job.title,
            'company_name':     job.company.company_name,
            'logo_path':        job.company.logo_path,
            'location':         job.location,
            'job_type':         job.job_type,
            'job_location_type':job.job_location_type,
            'experience_level': job.experience_level,
            'salary':           job.salary,
            'max_salary':       job.max_salary,
            'is_boosted':       job.is_boosted,
            'description':      job.description,
            'required_skills':  job.required_skills,
            'match_score':      match,
            'ats_score':        ats_data.get('score', 0) if ats_data else 0,
            'ats_findings':     ats_data.get('findings', []) if ats_data else [],
        })

    # Sort: boosted first, then by match score
    jobs.sort(key=lambda x: (x['is_boosted'], x['match_score']), reverse=True)

    # ── Applied jobs (right-swipes) ───────────────────────────────────────────
    swipes = (
        JobSwipe.query
        .filter_by(seeker_id=seeker.id, direction='right')
        .order_by(JobSwipe.created_at.desc())
        .all()
    )
    applications = [
        {
            'title':        sw.job_listing.title,
            'company_name': sw.job_listing.company.company_name,
            'applied_at':   sw.created_at,
            'status':       sw.status,
        }
        for sw in swipes
    ]

    return render_template(
        'seeker_dashboard.html',
        seeker=seeker,
        jobs=jobs,
        applications=applications,
        keywords=keywords,
    )


# ── Swipe (JSON endpoint) ─────────────────────────────────────────────────────
@seeker_bp.route('/swipe', methods=['POST'])
def swipe():
    if 'seeker_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    data      = request.get_json()
    job_id    = data.get('job_id')
    direction = data.get('direction')

    if not job_id or direction not in ('left', 'right'):
        return jsonify({'error': 'Invalid data'}), 400

    # Duplicate-swipe guard
    if JobSwipe.query.filter_by(seeker_id=session['seeker_id'], job_id=job_id).first():
        return jsonify({'status': 'already_swiped'})

    seeker = db.session.get(Seeker, session['seeker_id'])
    job    = db.session.get(JobListing, job_id)
    if not seeker or not job:
        return jsonify({'error': 'Not found'}), 404

    # AI scoring
    resume_text   = parse_resume(seeker.resume_path) if seeker.resume_path and os.path.exists(seeker.resume_path) else ''
    job_full_text = f'{job.title} {job.description} {job.required_skills}'
    m_score = match_resume_to_job(resume_text, job_full_text) if resume_text else 0
    a_score = calculate_ats_score(resume_text, job_full_text).get('score', 0) if resume_text else 0

    swipe_record = JobSwipe(
        seeker_id     = session['seeker_id'],
        job_id        = job_id,
        direction     = direction,
        status        = 'pending',
        match_score   = float(m_score),
        ats_score     = float(a_score),
        ai_rank_score = float(m_score * 0.7 + a_score * 0.3),
    )
    db.session.add(swipe_record)
    db.session.commit()

    if direction == 'right' and job.company:
        send_application_emails(
            seeker.email,
            f'{seeker.first_name} {seeker.last_name}',
            job.company.email,
            job.company.company_name,
            job.title,
            seeker.resume_path,
        )
        create_notification(
            user_id   = job.company_id,
            user_type = 'company',
            message   = f"New applicant: {seeker.first_name} {seeker.last_name} for '{job.title}'",
            type      = 'application',
        )

    return jsonify({'status': 'ok', 'direction': direction, 'match_score': m_score})


# ── Edit Seeker Profile ───────────────────────────────────────────────────────
@seeker_bp.route('/profile/seeker', methods=['GET', 'POST'])
def edit_seeker_profile():
    from flask import current_app

    seeker = _require_seeker()
    if not seeker:
        return redirect(url_for('auth.login_seeker'))

    if request.method == 'POST':
        resume_path = request.form.get('existing_resume', '')
        resume_file = request.files.get('resume')
        if resume_file and resume_file.filename and allowed_file(resume_file.filename, ALLOWED_RESUME):
            fname       = secure_filename(f'{uuid.uuid4()}_{resume_file.filename}')
            resume_path = os.path.join(current_app.config['RESUME_FOLDER'], fname)
            resume_file.save(resume_path)

        seeker.first_name  = request.form['first_name']
        seeker.last_name   = request.form['last_name']
        seeker.phone       = request.form.get('phone', '')
        seeker.education   = request.form.get('education', '')
        seeker.experience  = request.form.get('experience', '')
        seeker.skills      = request.form.get('skills', '')
        seeker.resume_path = resume_path

        db.session.commit()
        flash('Profile updated!', 'success')
        return redirect(url_for('seeker.seeker_dashboard'))

    return render_template('edit_seeker_profile.html', seeker=seeker)
