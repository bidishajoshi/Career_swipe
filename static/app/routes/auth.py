"""
app/routes/auth.py – Authentication routes.
Covers: home, resume upload, seeker/company registration & login, logout.
"""

import os
import uuid

from flask import (
    Blueprint, render_template, request, redirect,
    url_for, session, flash,
)
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

from ..extensions import db
from ..models import Seeker, Company
from ..utils.helpers import allowed_file
from ..utils.resume_parser import process_resume

auth_bp = Blueprint('auth', __name__)

ALLOWED_RESUME = {'pdf', 'doc', 'docx'}
ALLOWED_LOGO   = {'png', 'jpg', 'jpeg', 'webp'}


# ── Home ──────────────────────────────────────────────────────────────────────
@auth_bp.route('/')
def index():
    return render_template('index.html')


# ── Resume Upload (Step 1 of registration) ────────────────────────────────────
@auth_bp.route('/upload-resume', methods=['GET', 'POST'])
def upload_resume_step():
    from flask import current_app

    if request.method == 'POST':
        resume_file = request.files.get('resume')

        if not resume_file or not resume_file.filename:
            flash('No file selected.', 'error')
            return redirect(url_for('auth.upload_resume_step'))

        if not allowed_file(resume_file.filename, ALLOWED_RESUME):
            flash('Invalid file type. Please upload a PDF, DOC, or DOCX.', 'error')
            return redirect(url_for('auth.upload_resume_step'))

        fname       = secure_filename(f'{uuid.uuid4()}_{resume_file.filename}')
        resume_path = os.path.join(current_app.config['RESUME_FOLDER'], fname)
        resume_file.save(resume_path)

        extracted = process_resume(resume_path, current_app.config['RESUME_FOLDER'])

        if extracted:
            full_name = f"{extracted.get('first_name', '')} {extracted.get('last_name', '')}".strip()
            print(f'DEBUG resume extracted: {full_name} / {extracted.get("email")}', flush=True)

            session['resume_data'] = {
                'name':            full_name,
                'first_name':      extracted.get('first_name', ''),
                'last_name':       extracted.get('last_name', ''),
                'email':           extracted.get('email', ''),
                'phone':           extracted.get('phone', ''),
                'address':         extracted.get('address', ''),
                'gender':          extracted.get('gender', 'Other'),
                'dob':             extracted.get('dob', ''),
                'education':       extracted.get('education', ''),
                'experience':      extracted.get('experience', ''),
                'experience_type': extracted.get('experience_type', 'Full-time'),
                'career_field':    extracted.get('career_field', 'Other'),
                'job_location_type': extracted.get('job_location_type', 'Local'),
                'desired_roles':   extracted.get('desired_roles', ''),
                'employment_type': extracted.get('employment_type', 'Full-time'),
                'salary':          extracted.get('salary', ''),
                'availability':    extracted.get('availability', 'Immediate'),
                'skills':          extracted.get('skills', ''),
                'resume_path':     resume_path,
            }
            flash('Resume analysed! Please verify your information.', 'success')
        else:
            flash("We couldn't extract all details – you can fill them in manually.", 'warning')
            session['resume_data'] = {'resume_path': resume_path}

        session.modified = True
        return redirect(url_for('auth.register_seeker'))

    return render_template('upload_resume.html')


# ── Seeker Registration ───────────────────────────────────────────────────────
@auth_bp.route('/register/seeker', methods=['GET', 'POST'])
def register_seeker():
    from flask import current_app

    resume_data = session.get('resume_data', {})
    print(f'DEBUG session resume_data: {resume_data}', flush=True)

    if request.method == 'POST':
        email = request.form['email'].strip().lower()

        if Seeker.query.filter_by(email=email).first():
            flash('Email already registered.', 'error')
            return redirect(url_for('auth.register_seeker'))

        # Allow resume replacement at registration step
        resume_path = resume_data.get('resume_path', '')
        resume_file = request.files.get('resume')
        if resume_file and resume_file.filename and allowed_file(resume_file.filename, ALLOWED_RESUME):
            fname       = secure_filename(f'{uuid.uuid4()}_{resume_file.filename}')
            resume_path = os.path.join(current_app.config['RESUME_FOLDER'], fname)
            resume_file.save(resume_path)

        seeker = Seeker(
            first_name        = request.form['first_name'],
            last_name         = request.form['last_name'],
            email             = email,
            password_hash     = generate_password_hash(request.form['password']),
            phone             = request.form.get('phone', ''),
            address           = request.form.get('address', ''),
            education         = request.form.get('education', ''),
            experience        = request.form.get('experience', ''),
            skills            = request.form.get('skills', ''),
            resume_path       = resume_path,
            gender            = request.form.get('gender'),
            dob               = request.form.get('dob'),
            experience_type   = request.form.get('experience_type'),
            career_field      = request.form.get('career_field'),
            job_status        = request.form.get('job_status', 'Searching'),
            job_location_type = request.form.get('job_location_type'),
            desired_roles     = request.form.get('desired_roles'),
            salary_expectation= request.form.get('salary'),
            availability      = request.form.get('availability'),
            is_verified       = True,
        )
        db.session.add(seeker)
        db.session.commit()
        session.pop('resume_data', None)

        flash('Account created! You can log in now.', 'success')
        return redirect(url_for('auth.login_seeker'))

    return render_template(
        'register_seeker.html',
        name             = resume_data.get('name'),
        first_name       = resume_data.get('first_name'),
        last_name        = resume_data.get('last_name'),
        email            = resume_data.get('email'),
        phone            = resume_data.get('phone'),
        address          = resume_data.get('address'),
        gender           = resume_data.get('gender'),
        dob              = resume_data.get('dob'),
        education        = resume_data.get('education'),
        experience       = resume_data.get('experience'),
        experience_type  = resume_data.get('experience_type'),
        career_field     = resume_data.get('career_field'),
        job_location_type= resume_data.get('job_location_type'),
        desired_roles    = resume_data.get('desired_roles'),
        employment_type  = resume_data.get('employment_type'),
        salary           = resume_data.get('salary'),
        availability     = resume_data.get('availability'),
        skills           = resume_data.get('skills'),
        resume_path      = resume_data.get('resume_path'),
    )


# ── Company Registration ──────────────────────────────────────────────────────
@auth_bp.route('/register/company', methods=['GET', 'POST'])
def register_company():
    from flask import current_app

    if request.method == 'POST':
        email = request.form['email'].strip().lower()

        if Company.query.filter_by(email=email).first():
            flash('Email already registered.', 'error')
            return redirect(url_for('auth.register_company'))

        logo_path = ''
        logo_file = request.files.get('logo')
        if logo_file and logo_file.filename and allowed_file(logo_file.filename, ALLOWED_LOGO):
            fname     = secure_filename(f'{uuid.uuid4()}_{logo_file.filename}')
            logo_path = os.path.join(current_app.config['LOGO_FOLDER'], fname)
            logo_file.save(logo_path)

        company = Company(
            company_name  = request.form['company_name'],
            email         = email,
            password_hash = generate_password_hash(request.form['password']),
            description   = request.form.get('description', ''),
            industry      = request.form.get('industry', ''),
            website       = request.form.get('website', ''),
            logo_path     = logo_path,
            is_verified   = True,
        )
        db.session.add(company)
        db.session.commit()

        flash('Company registered!', 'success')
        return redirect(url_for('auth.login_company'))

    return render_template('register_company.html')


# ── Seeker Login ──────────────────────────────────────────────────────────────
@auth_bp.route('/login/seeker', methods=['GET', 'POST'])
def login_seeker():
    if request.method == 'POST':
        email = request.form['email'].strip().lower()
        user  = Seeker.query.filter_by(email=email).first()

        if user and check_password_hash(user.password_hash, request.form['password']):
            session['seeker_id']   = user.id
            session['seeker_name'] = user.first_name
            return redirect(url_for('seeker.seeker_dashboard'))

        flash('Invalid email or password.', 'error')
    return render_template('login_seeker.html')


# ── Company Login ─────────────────────────────────────────────────────────────
@auth_bp.route('/login/company', methods=['GET', 'POST'])
def login_company():
    if request.method == 'POST':
        email = request.form['email'].strip().lower()
        co    = Company.query.filter_by(email=email).first()

        if co and check_password_hash(co.password_hash, request.form['password']):
            session['company_id']   = co.id
            session['company_name'] = co.company_name
            return redirect(url_for('company.company_dashboard'))

        flash('Invalid email or password.', 'error')
    return render_template('login_company.html')


# ── Logout ────────────────────────────────────────────────────────────────────
@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.index'))
