"""
app/routes/jobs.py – Job listing routes.
Covers: post a job (company only).
"""

from flask import (
    Blueprint, render_template, request, redirect,
    url_for, session, flash,
)

from ..extensions import db
from ..models import JobListing

jobs_bp = Blueprint('jobs', __name__)


@jobs_bp.route('/jobs/post', methods=['GET', 'POST'])
def post_job():
    if 'company_id' not in session:
        return redirect(url_for('auth.login_company'))

    if request.method == 'POST':
        job = JobListing(
            company_id        = session['company_id'],
            title             = request.form['title'],
            description       = request.form['description'],
            required_skills   = request.form.get('required_skills', ''),
            location          = request.form.get('location', ''),
            job_type          = request.form.get('job_type', 'Full-time'),
            job_location_type = request.form.get('job_location_type', 'Onsite'),
            experience_level  = request.form.get('experience_level', 'Entry Level'),
            min_experience    = request.form.get('min_experience', 0, type=int),
            salary            = request.form.get('salary', ''),
            max_salary        = request.form.get('max_salary', 0, type=int),
            tags              = request.form.get('tags', ''),
        )
        db.session.add(job)
        db.session.commit()
        flash('Job posted successfully!', 'success')
        return redirect(url_for('company.company_dashboard'))

    return render_template('post_job.html')
