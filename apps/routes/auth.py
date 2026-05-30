"""
app/routes/auth.py – Authentication routes.
Covers: home, resume upload, seeker/company registration & login, logout.
"""

import json
import os
import uuid

from flask import (
    Blueprint, render_template, request, redirect,
    url_for, session, flash,
)
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

from ..extensions import db
from ..models import Seeker, Company, EligibilityQuestion
from ..services import EligibilityService
from utils.helpers import allowed_file
from utils.resume_parser import process_resume
from utils.profile_helpers import update_seeker_completion, update_company_completion

auth_bp = Blueprint('auth', __name__)

ALLOWED_RESUME = {'pdf', 'doc', 'docx', 'txt'}
ALLOWED_LOGO   = {'png', 'jpg', 'jpeg', 'webp'}
ALLOWED_PHOTO  = {'png', 'jpg', 'jpeg', 'webp'}
ALLOWED_DOC    = {'pdf', 'doc', 'docx', 'png', 'jpg', 'jpeg'}


def normalize_file_path(file_path):
    """Convert file path to web-safe relative path with forward slashes."""
    if not file_path:
        return ''
    return file_path.replace('\\', '/').replace('static/', '')


def safe_check_password(password_hash, password):
    """Reject invalid credentials without crashing on malformed legacy hashes."""
    if not password_hash or not password:
        return False
    try:
        return check_password_hash(password_hash, password)
    except (TypeError, ValueError):
        return False


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
            resume_path = extracted.get('resume_path', resume_path)

        if extracted:
            full_name = f"{extracted.get('first_name', '')} {extracted.get('last_name', '')}".strip()
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
    eligibility_questions = EligibilityQuestion.query.filter_by(
        is_active=True
    ).order_by(EligibilityQuestion.display_order).all()

    if not eligibility_questions:
        EligibilityService.create_eligibility_questions()
        eligibility_questions = EligibilityQuestion.query.filter_by(
            is_active=True
        ).order_by(EligibilityQuestion.display_order).all()

    if request.method == 'POST':
        email = request.form['email'].strip().lower()

        if Seeker.query.filter_by(email=email).first():
            flash('Email already registered.', 'error')
            return redirect(url_for('auth.register_seeker'))

        required_fields = [
            'first_name', 'last_name', 'email', 'password', 'phone',
            'address', 'education', 'experience', 'experience_type',
            'skills', 'career_field', 'desired_roles', 'employment_type',
            'job_location_type', 'salary', 'availability'
        ]
        missing_fields = [field for field in required_fields if not request.form.get(field, '').strip()]
        if missing_fields:
            flash('Please complete all required fields before submitting your application.', 'error')
            return redirect(url_for('auth.register_seeker'))

        missing_answers = []
        for question in eligibility_questions:
            field_name = f'question_{question.id}'
            value = request.form.get(field_name)
            if question.is_mandatory and (not value or str(value).strip() == ''):
                missing_answers.append(question.question_text)

        if missing_answers:
            flash(
                'Please answer the required eligibility questions: ' + ', '.join(missing_answers),
                'error'
            )
            return redirect(url_for('auth.register_seeker'))

        if not request.form.get('age_verified') or not request.form.get('legally_eligible'):
            flash('Please confirm eligibility requirements.', 'error')
            return redirect(url_for('auth.register_seeker'))

        resume_path = request.form.get('existing_resume') or resume_data.get('resume_path', '')
        resume_file = request.files.get('resume')
        if resume_file and resume_file.filename:
            if not allowed_file(resume_file.filename, ALLOWED_RESUME):
                flash('Invalid resume file type. Please upload a PDF, DOC, or DOCX.', 'error')
                return redirect(url_for('auth.register_seeker'))
            fname       = secure_filename(f'{uuid.uuid4()}_{resume_file.filename}')
            resume_path = os.path.join(current_app.config['RESUME_FOLDER'], fname)
            resume_file.save(resume_path)
            converted = process_resume(resume_path, current_app.config['RESUME_FOLDER'])
            if converted:
                resume_path = converted.get('resume_path', resume_path)

        if not resume_path:
            flash('Resume is required. Please upload your resume before submitting.', 'error')
            return redirect(url_for('auth.register_seeker'))

        profile_photo_path = ''
        photo_file = request.files.get('profile_photo')
        if photo_file and photo_file.filename and allowed_file(photo_file.filename, ALLOWED_PHOTO):
            fname = secure_filename(f'{uuid.uuid4()}_{photo_file.filename}')
            photo_path = os.path.join(current_app.config['LOGO_FOLDER'], fname)
            photo_file.save(photo_path)
            profile_photo_path = normalize_file_path(photo_path)

        seeker = Seeker(
            first_name         = request.form['first_name'],
            last_name          = request.form['last_name'],
            email              = email,
            password_hash      = generate_password_hash(request.form['password']),
            phone              = request.form.get('phone', ''),
            address            = request.form.get('address', ''),
            country            = request.form.get('country', ''),
            linkedin           = request.form.get('linkedin', ''),
            portfolio          = request.form.get('portfolio', ''),
            profile_photo_path = profile_photo_path,
            education          = request.form.get('education', ''),
            education_history  = request.form.get('education_history', ''),
            experience         = request.form.get('experience', ''),
            skills             = request.form.get('skills', ''),
            certifications     = request.form.get('certifications', ''),
            resume_path        = normalize_file_path(resume_path),
            employment_type    = request.form.get('employment_type', ''),
            source             = request.form.get('source', ''),
            gender             = request.form.get('gender'),
            dob                = request.form.get('dob'),
            experience_type    = request.form.get('experience_type'),
            career_field       = request.form.get('career_field'),
            job_status         = request.form.get('job_status', 'Searching'),
            job_location_type  = request.form.get('job_location_type'),
            desired_roles      = request.form.get('desired_roles'),
            salary_expectation = request.form.get('salary'),
            availability       = request.form.get('availability'),
            age_verified       = 'age_verified' in request.form,
            legally_eligible   = 'legally_eligible' in request.form,
            is_verified        = True,
            is_published       = True,
        )
        update_seeker_completion(seeker)
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
        country          = resume_data.get('country'),
        gender           = resume_data.get('gender'),
        dob              = resume_data.get('dob'),
        education        = resume_data.get('education'),
        experience       = resume_data.get('experience'),
        experience_type  = resume_data.get('experience_type'),
        career_field     = resume_data.get('career_field'),
        job_location_type= resume_data.get('job_location_type'),
        desired_roles    = resume_data.get('desired_roles'),
        employment_type  = resume_data.get('employment_type'),
        salary           = request.form.get('salary') if request.method == 'POST' else resume_data.get('salary'),
        availability     = request.form.get('availability') if request.method == 'POST' else resume_data.get('availability'),
        skills           = request.form.get('skills') if request.method == 'POST' else resume_data.get('skills'),
        resume_path      = resume_data.get('resume_path'),
        eligibility_questions = [q.to_dict() for q in eligibility_questions],
    )


# ── Company Registration ──────────────────────────────────────────────────────
@auth_bp.route('/register/company', methods=['GET', 'POST'])
def register_company():
    from flask import current_app

    if request.method == 'POST':
        email = request.form['email'].strip().lower()
        password = request.form.get('password', '')

        if len(password) < 8:
            flash('Password must be at least 8 characters.', 'error')
            return redirect(url_for('auth.register_company'))

        if Company.query.filter_by(email=email).first():
            flash('Email already registered.', 'error')
            return redirect(url_for('auth.register_company'))

        if not request.form.get('age_verified') or not request.form.get('legally_eligible'):
            flash('Please confirm eligibility requirements.', 'error')
            return redirect(url_for('auth.register_company'))

        logo_file = request.files.get('logo')
        if not logo_file or not logo_file.filename:
            flash('Company logo is required.', 'error')
            return redirect(url_for('auth.register_company'))

        if not allowed_file(logo_file.filename, ALLOWED_LOGO):
            flash('Invalid logo format. Please upload PNG, JPG, or WEBP.', 'error')
            return redirect(url_for('auth.register_company'))

        fname = secure_filename(f'{uuid.uuid4()}_{logo_file.filename}')
        logo_full_path = os.path.join(current_app.config['LOGO_FOLDER'], fname)
        logo_file.save(logo_full_path)
        logo_path = normalize_file_path(logo_full_path)

        verification_doc = ''
        verification_file = request.files.get('verification_document')
        if verification_file and verification_file.filename and allowed_file(verification_file.filename, ALLOWED_DOC):
            vfname = secure_filename(f'{uuid.uuid4()}_{verification_file.filename}')
            vpath = os.path.join(current_app.config['UPLOAD_FOLDER'], vfname)
            verification_file.save(vpath)
            verification_doc = normalize_file_path(vpath)

        company = Company(
            company_name     = request.form.get('company_name', ''),
            email            = email,
            password_hash    = generate_password_hash(password),
            phone            = request.form.get('phone', ''),
            company_address  = request.form.get('company_address', ''),
            country          = request.form.get('country', ''),
            industry         = request.form.get('industry', ''),
            company_size     = request.form.get('company_size', ''),
            website          = request.form.get('website', ''),
            description      = request.form.get('description', ''),
            mission          = request.form.get('mission', ''),
            culture          = request.form.get('culture', ''),
            perks            = request.form.get('perks', ''),
            work_mode        = request.form.get('work_mode', ''),
            open_positions   = request.form.get('open_positions', ''),
            hiring_categories= request.form.get('hiring_categories', ''),
            linkedin_url     = request.form.get('linkedin_url', ''),
            business_registration = request.form.get('business_registration', ''),
            logo_path        = logo_path,
            verification_document = verification_doc,
            is_verified      = True,
            age_verified     = 'age_verified' in request.form,
            legally_eligible = 'legally_eligible' in request.form,
            is_published     = True,
            notification_enabled = True,
        )
        update_company_completion(company)
        db.session.add(company)
        db.session.commit()

        flash('Company registered successfully! You can now log in.', 'success')
        return redirect(url_for('auth.login_company'))

    return render_template('register_company.html')


# ── Seeker Login ──────────────────────────────────────────────────────────────
@auth_bp.route('/login/seeker', methods=['GET', 'POST'])
def login_seeker():
    if request.method == 'POST':
        email = request.form['email'].strip().lower()
        user  = Seeker.query.filter_by(email=email).first()

        if user and safe_check_password(user.password_hash, request.form.get('password', '')):
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

        if co and safe_check_password(co.password_hash, request.form.get('password', '')):
            session['company_id']   = co.id
            session['company_name'] = co.company_name
            return redirect(url_for('company.company_dashboard'))

        flash('Invalid email or password.', 'error')
    return render_template('login_company.html')


# ── Logout ────────────────────────────────────────────────────────────────────
@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))
