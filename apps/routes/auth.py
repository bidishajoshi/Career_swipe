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
from ..models import Seeker, Company, EligibilityQuestion
from ..services import EligibilityService
from utils.helpers import allowed_file
from utils.resume_parser import process_resume

auth_bp = Blueprint('auth', __name__)

ALLOWED_RESUME = {'pdf', 'doc', 'docx'}
ALLOWED_LOGO   = {'png', 'jpg', 'jpeg', 'webp'}


def normalize_file_path(file_path):
    """Convert file path to web-safe relative path with forward slashes."""
    if not file_path:
        return ''
    return file_path.replace('\\', '/').replace('static/', '')


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

        # Allow resume replacement at registration step
        resume_path = resume_data.get('resume_path', '')
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

        if Company.query.filter_by(email=email).first():
            flash('Email already registered.', 'error')
            return redirect(url_for('auth.register_company'))

        # Validate passwords match
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        if password != confirm_password:
            flash('Passwords do not match.', 'error')
            return redirect(url_for('auth.register_company'))

        # Handle logo upload (REQUIRED)
        logo_path = ''
        logo_file = request.files.get('logo')
        if not logo_file or not logo_file.filename:
            flash('Company logo is required.', 'error')
            return redirect(url_for('auth.register_company'))
        
        if not allowed_file(logo_file.filename, ALLOWED_LOGO):
            flash('Invalid logo format. Please upload a PNG or JPG file.', 'error')
            return redirect(url_for('auth.register_company'))
            
        fname     = secure_filename(f'{uuid.uuid4()}_{logo_file.filename}')
        logo_full_path = os.path.join(current_app.config['LOGO_FOLDER'], fname)
        logo_file.save(logo_full_path)
        # Store relative path for web serving (uploads/logos/filename)
        logo_path = normalize_file_path(logo_full_path)

        # Handle banner upload
        banner_path = ''
        banner_file = request.files.get('banner')
        if banner_file and banner_file.filename and allowed_file(banner_file.filename, ALLOWED_LOGO):
            fname       = secure_filename(f'{uuid.uuid4()}_{banner_file.filename}')
            banner_full_path = os.path.join(current_app.config['LOGO_FOLDER'], fname)
            banner_file.save(banner_full_path)
            banner_path = normalize_file_path(banner_full_path)

        # Handle verification document upload
        verification_doc = ''
        verification_file = request.files.get('verification_document')
        if verification_file and verification_file.filename:
            fname            = secure_filename(f'{uuid.uuid4()}_{verification_file.filename}')
            verification_full_path = os.path.join(current_app.config['UPLOAD_FOLDER'], fname)
            verification_file.save(verification_full_path)
            verification_doc = normalize_file_path(verification_full_path)

        # Create company with all fields
        company = Company(
            # Basic Information
            company_name     = request.form.get('company_name', ''),
            email            = email,
            password_hash    = generate_password_hash(password),
            phone            = request.form.get('phone', ''),
            hr_name          = request.form.get('hr_name', ''),
            
            # Company details
            company_type     = request.form.get('company_type', ''),
            industry         = request.form.get('industry', ''),
            company_size     = request.form.get('company_size', ''),
            founded_year     = request.form.get('founded_year', type=int) if request.form.get('founded_year') else None,
            headquarters     = request.form.get('headquarters', ''),
            country          = request.form.get('country', ''),
            website          = request.form.get('website', ''),
            
            # Description sections
            description      = request.form.get('description', ''),
            mission          = request.form.get('mission', ''),
            vision           = request.form.get('vision', ''),
            culture          = request.form.get('culture', ''),
            perks            = request.form.get('perks', ''),
            
            # Hiring information
            hiring_frequency = request.form.get('hiring_frequency', ''),
            remote_hiring    = 'remote_hiring' in request.form,
            international_hiring = 'international_hiring' in request.form,
            preferred_locations = request.form.get('preferred_locations', ''),
            
            # Media
            logo_path        = logo_path,
            banner_path      = banner_path,
            verification_document = verification_doc,
            
            # Social links
            linkedin_url     = request.form.get('linkedin_url', ''),
            facebook_url     = request.form.get('facebook_url', ''),
            instagram_url    = request.form.get('instagram_url', ''),
            twitter_url      = request.form.get('twitter_url', ''),
            youtube_url      = request.form.get('youtube_url', ''),
            
            # Status
            profile_completion = 100,
            is_verified      = True,
            age_verified     = 'age_verified' in request.form,
            legally_eligible = 'legally_eligible' in request.form,
            notification_enabled = True,
        )
        
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
