"""
app/routes/company.py – Company-facing routes.
Covers: company dashboard, post job, applicant status update, profile management.
"""

import os
import uuid
from werkzeug.security import generate_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime

from flask import (
    Blueprint, render_template, request, redirect,
    url_for, session, flash, current_app,
)

from ..extensions import db
from ..models import Company, JobListing, JobSwipe, Notification
from ..services.email_service import send_status_update_email
from ..services.notification_service import create_notification
from utils.applicant_presenter import build_applicant_cards, existing_static_path
from utils.helpers import allowed_file

company_bp = Blueprint('company', __name__)

# Map URL action → DB status string
ACTION_MAP = {
    'shortlist': 'shortlisted',
    'interview': 'interview',
    'accept':    'accepted',
    'reject':    'rejected',
}


def _require_company():
    """Return the logged-in Company or None (also clears invalid session)."""
    company_id = session.get('company_id')
    if not company_id:
        return None
    company = db.session.get(Company, company_id)
    if not company:
        session.clear()
    return company


# ── Company Dashboard ─────────────────────────────────────────────────────────
@company_bp.route('/dashboard/company', endpoint='company_dashboard')
def company_dashboard():
    company = _require_company()
    if not company:
        return redirect(url_for('auth.login_company'))
    company.logo_path = existing_static_path(company.logo_path)

    jobs = (
        JobListing.query
        .filter_by(company_id=company.id)
        .order_by(JobListing.created_at.desc())
        .all()
    )

    swipes = (
        JobSwipe.query
        .join(JobListing)
        .filter(
            JobListing.company_id == company.id,
            JobSwipe.direction == 'right',
        )
        .order_by(JobSwipe.created_at.desc())
        .all()
    )

    job_application_counts = {job.id: 0 for job in jobs}
    job_accepted_counts = {job.id: 0 for job in jobs}
    for sw in swipes:
        if sw.job_id in job_application_counts:
            job_application_counts[sw.job_id] += 1
            if sw.status == 'accepted':
                job_accepted_counts[sw.job_id] += 1

    for job in jobs:
        job.application_count = job_application_counts.get(job.id, 0)
        job.accepted_count = job_accepted_counts.get(job.id, 0)

    applicants = build_applicant_cards(swipes)

    return render_template(
        'company_dashboard.html',
        company=company,
        jobs=jobs,
        applicants=applicants,
    )


# ── Company Insights (Tile drill-down) ───────────────────────────────────────
@company_bp.route('/company/insights', endpoint='company_insights')
def company_insights():
    company = _require_company()
    if not company:
        return redirect(url_for('auth.login_company'))

    tab = (request.args.get('tab') or 'jobs').lower()
    valid_tabs = {'jobs', 'applications', 'shortlisted', 'interview'}
    if tab not in valid_tabs:
        tab = 'jobs'

    jobs = (
        JobListing.query
        .filter_by(company_id=company.id)
        .order_by(JobListing.created_at.desc())
        .all()
    )

    swipes = (
        JobSwipe.query
        .join(JobListing)
        .filter(
            JobListing.company_id == company.id,
            JobSwipe.direction == 'right',
        )
        .order_by(JobSwipe.created_at.desc())
        .all()
    )

    if tab == 'shortlisted':
        swipes = [sw for sw in swipes if (sw.status or '').lower() == 'shortlisted']
    elif tab == 'interview':
        swipes = [sw for sw in swipes if (sw.status or '').lower() == 'interview']

    applicants = build_applicant_cards(swipes)

    return render_template(
        'company_insights.html',
        company=company,
        jobs=jobs,
        applicants=applicants,
        tab=tab,
    )


# ── Update Applicant Status ───────────────────────────────────────────────────
@company_bp.route('/applicant/<int:swipe_id>/<action>', endpoint='update_applicant')
def update_applicant(swipe_id, action):
    company = _require_company()
    if not company:
        return redirect(url_for('auth.login_company'))

    swipe = db.session.get(JobSwipe, swipe_id)
    if not swipe:
        flash('Applicant not found.', 'error')
        return redirect(url_for('company.company_dashboard'))

    if swipe.job_listing.company_id != company.id:
        flash('Unauthorized action.', 'error')
        return redirect(url_for('company.company_dashboard'))

    action_text  = ACTION_MAP.get(action, action + 'ed')
    swipe.status = action_text
    db.session.commit()

    seeker = swipe.seeker
    job    = swipe.job_listing
    positions_needed = getattr(job, 'number_of_positions', None) or getattr(job, 'number_of_vacancies', None) or 1

    # Send status-update email to seeker (accepted/rejected only)
    if action_text in ('accepted', 'rejected'):
        send_status_update_email(
            seeker_email=seeker.email,
            seeker_name=seeker.first_name,
            job_title=job.title,
            company_name=job.company.company_name,
            new_status=action_text,
        )

    # Build a meaningful in-app notification
    if action == 'accept':
        notif_msg = (
            f"Congratulations! Your application for {job.title} "
            f"at {job.company.company_name} has been ACCEPTED."
        )
    elif action == 'interview':
        notif_msg = (
            f"Interview Scheduled! {job.company.company_name} wants to "
            f"interview you for {job.title}."
        )
    else:
        notif_msg = (
            f"Your application for {job.title} at {job.company.company_name} "
            f"has been {action_text}."
        )

    create_notification(
        user_id   = seeker.id,
        user_type = 'seeker',
        message   = notif_msg,
        type      = action,
    )

    if action == 'accept':
        accepted_count = JobSwipe.query.filter_by(job_id=job.id, status='accepted').count()
        if accepted_count >= positions_needed:
            job_title = job.title
            db.session.delete(job)
            db.session.commit()
            flash(
                f'Applicant {action_text}. Job "{job_title}" is now filled and has been closed.',
                'success',
            )
            return redirect(url_for('company.company_dashboard'))

    flash(f'Applicant {action_text}.', 'success')
    return redirect(url_for('company.company_dashboard'))
