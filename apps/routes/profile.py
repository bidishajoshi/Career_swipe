"""
Profile wizard routes – role selection, autosave, company profile management.
"""

import json
import os
import uuid
from datetime import datetime

from flask import (
    Blueprint, render_template, request, redirect,
    url_for, session, flash, jsonify, current_app,
)
from werkzeug.security import generate_password_hash
from werkzeug.utils import secure_filename

from ..extensions import db
from ..models import Seeker, Company
from utils.helpers import allowed_file
from utils.profile_helpers import update_seeker_completion, update_company_completion

profile_bp = Blueprint('profile', __name__)

ALLOWED_RESUME = {'pdf', 'doc', 'docx', 'txt'}
ALLOWED_LOGO = {'png', 'jpg', 'jpeg', 'webp'}
ALLOWED_PHOTO = {'png', 'jpg', 'jpeg', 'webp'}
ALLOWED_DOC = {'pdf', 'doc', 'docx', 'png', 'jpg', 'jpeg'}


def normalize_file_path(file_path):
    if not file_path:
        return ''
    return file_path.replace('\\', '/').replace('static/', '')


def _require_seeker():
    seeker_id = session.get('seeker_id')
    if not seeker_id:
        return None
    return db.session.get(Seeker, seeker_id)


def _require_company():
    company_id = session.get('company_id')
    if not company_id:
        return None
    return db.session.get(Company, company_id)


@profile_bp.route('/register')
def register_role():
    """Step 1: Role selection for multi-role profile wizard."""
    return render_template('register_role.html')


@profile_bp.route('/api/profile/autosave', methods=['POST'])
def autosave_draft():
    """Save registration wizard progress to session (pre-account)."""
    role = request.form.get('role', 'seeker')
    data = {k: v for k, v in request.form.items() if k != 'role'}
    key = f'{role}_draft'
    session[key] = data
    session.modified = True
    return jsonify({
        'ok': True,
        'saved_at': datetime.utcnow().strftime('%H:%M'),
        'completion': len([v for v in data.values() if v and str(v).strip()]),
    })


@profile_bp.route('/api/profile/seeker/autosave', methods=['POST'])
def autosave_seeker_profile():
    seeker = _require_seeker()
    if not seeker:
        return jsonify({'error': 'Unauthorized'}), 401

    for field in (
        'first_name', 'last_name', 'phone', 'address', 'country',
        'linkedin', 'portfolio', 'education', 'education_history',
        'experience', 'skills', 'certifications', 'career_field',
        'desired_roles', 'employment_type', 'job_location_type',
        'salary_expectation', 'availability', 'gender', 'dob',
    ):
        if field in request.form:
            setattr(seeker, field, request.form.get(field, ''))

    pct = update_seeker_completion(seeker)
    seeker.draft_data = json.dumps(dict(request.form))
    db.session.commit()
    return jsonify({'ok': True, 'profile_completion': pct})


@profile_bp.route('/api/profile/company/autosave', methods=['POST'])
def autosave_company_profile():
    company = _require_company()
    if not company:
        return jsonify({'error': 'Unauthorized'}), 401

    text_fields = (
        'company_name', 'phone', 'company_address', 'headquarters', 'country',
        'industry', 'company_size', 'company_type', 'website', 'description',
        'mission', 'vision', 'culture', 'perks', 'hiring_frequency',
        'preferred_locations', 'hiring_categories', 'work_mode',
        'open_positions', 'linkedin_url', 'facebook_url', 'instagram_url',
        'twitter_url', 'business_registration',
    )
    for field in text_fields:
        if field in request.form:
            setattr(company, field, request.form.get(field, ''))

    if 'number_of_vacancies' in request.form:
        try:
            company.number_of_vacancies = int(request.form.get('number_of_vacancies') or 0)
        except ValueError:
            pass

    company.remote_hiring = 'remote_hiring' in request.form
    company.international_hiring = 'international_hiring' in request.form

    pct = update_company_completion(company)
    company.draft_data = json.dumps(dict(request.form))
    db.session.commit()
    return jsonify({'ok': True, 'profile_completion': pct})


@profile_bp.route('/profile/company', methods=['GET', 'POST'])
def edit_company_profile():
    company = _require_company()
    if not company:
        return redirect(url_for('auth.login_company'))

    if request.method == 'POST':
        action = request.form.get('action', 'save')

        company.company_name = request.form.get('company_name', company.company_name)
        company.phone = request.form.get('phone', '')
        company.company_address = request.form.get('company_address', '')
        company.headquarters = request.form.get('headquarters', '')
        company.country = request.form.get('country', '')
        company.industry = request.form.get('industry', '')
        company.company_size = request.form.get('company_size', '')
        company.company_type = request.form.get('company_type', '')
        company.website = request.form.get('website', '')
        company.hr_name = request.form.get('hr_name', '')
        company.description = request.form.get('description', '')
        company.mission = request.form.get('mission', '')
        company.vision = request.form.get('vision', '')
        company.culture = request.form.get('culture', '')
        company.perks = request.form.get('perks', '')
        company.hiring_frequency = request.form.get('hiring_frequency', '')
        company.preferred_locations = request.form.get('preferred_locations', '')
        company.hiring_categories = request.form.get('hiring_categories', '')
        company.work_mode = request.form.get('work_mode', '')
        company.open_positions = request.form.get('open_positions', '')
        company.linkedin_url = request.form.get('linkedin_url', '')
        company.facebook_url = request.form.get('facebook_url', '')
        company.instagram_url = request.form.get('instagram_url', '')
        company.twitter_url = request.form.get('twitter_url', '')
        company.youtube_url = request.form.get('youtube_url', '')
        company.business_registration = request.form.get('business_registration', '')
        company.remote_hiring = 'remote_hiring' in request.form
        company.international_hiring = 'international_hiring' in request.form
        company.notification_enabled = 'notification_enabled' in request.form

        if request.form.get('founded_year'):
            try:
                company.founded_year = int(request.form.get('founded_year'))
            except ValueError:
                pass
        if request.form.get('number_of_vacancies'):
            try:
                company.number_of_vacancies = int(request.form.get('number_of_vacancies'))
            except ValueError:
                pass

        # File uploads
        logo_file = request.files.get('logo')
        if logo_file and logo_file.filename and allowed_file(logo_file.filename, ALLOWED_LOGO):
            fname = secure_filename(f'{uuid.uuid4()}_{logo_file.filename}')
            path = os.path.join(current_app.config['LOGO_FOLDER'], fname)
            logo_file.save(path)
            company.logo_path = normalize_file_path(path)

        banner_file = request.files.get('banner')
        if banner_file and banner_file.filename and allowed_file(banner_file.filename, ALLOWED_LOGO):
            fname = secure_filename(f'{uuid.uuid4()}_{banner_file.filename}')
            path = os.path.join(current_app.config['LOGO_FOLDER'], fname)
            banner_file.save(path)
            company.banner_path = normalize_file_path(path)

        gallery_files = request.files.getlist('gallery')
        gallery_paths = json.loads(company.gallery_paths or '[]')
        for gf in gallery_files:
            if gf and gf.filename and allowed_file(gf.filename, ALLOWED_LOGO):
                fname = secure_filename(f'{uuid.uuid4()}_{gf.filename}')
                path = os.path.join(current_app.config['LOGO_FOLDER'], fname)
                gf.save(path)
                gallery_paths.append(normalize_file_path(path))
        if gallery_paths:
            company.gallery_paths = json.dumps(gallery_paths)

        ver_file = request.files.get('verification_document')
        if ver_file and ver_file.filename and allowed_file(ver_file.filename, ALLOWED_DOC):
            fname = secure_filename(f'{uuid.uuid4()}_{ver_file.filename}')
            path = os.path.join(current_app.config['UPLOAD_FOLDER'], fname)
            ver_file.save(path)
            company.verification_document = normalize_file_path(path)

        if action == 'publish':
            company.is_published = True
            flash('Company profile published!', 'success')
        elif action == 'draft':
            company.is_published = False
            flash('Profile saved as draft.', 'success')
        else:
            flash('Profile updated!', 'success')

        update_company_completion(company)
        db.session.commit()
        return redirect(url_for('profile.edit_company_profile'))

    if company.profile_completion is None:
        update_company_completion(company)
        db.session.commit()

    return render_template('edit_company_profile.html', company=company)
