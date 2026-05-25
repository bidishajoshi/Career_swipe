"""
app/routes/company.py – Company-facing routes.
Covers: company dashboard, post job, applicant status update.
"""

from flask import (
    Blueprint, render_template, request, redirect,
    url_for, session, flash,
)

from ..extensions import db
from ..models import Company, JobListing, JobSwipe
from ..services.email_service import send_status_update_email
from ..services.notification_service import create_notification

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
@company_bp.route('/dashboard/company')
def company_dashboard():
    company = _require_company()
    if not company:
        return redirect(url_for('auth.login_company'))

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

    applicants = [
        {
            'seeker_id':   sw.seeker.id,
            'first_name':  sw.seeker.first_name,
            'last_name':   sw.seeker.last_name,
            'email':       sw.seeker.email,
            'skills':      sw.seeker.skills,
            'resume_path': sw.seeker.resume_path,
            'job_title':   sw.job_listing.title,
            'applied_at':  sw.created_at,
            'status':      sw.status,
            'swipe_id':    sw.id,
            'match_score': sw.match_score,
            'ats_score':   sw.ats_score,
        }
        for sw in swipes
    ]

    return render_template(
        'company_dashboard.html',
        company=company,
        jobs=jobs,
        applicants=applicants,
    )


# ── Update Applicant Status ───────────────────────────────────────────────────
@company_bp.route('/applicant/<int:swipe_id>/<action>')
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

    # Send status-update email to seeker
    send_status_update_email(
        seeker_email=seeker.email,
        seeker_name=seeker.first_name,
        job_title=job.title,
        company_name=job.company.company_name,
        action_text=action_text,
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

    flash(f'Applicant {action_text}.', 'success')
    return redirect(url_for('company.company_dashboard'))
