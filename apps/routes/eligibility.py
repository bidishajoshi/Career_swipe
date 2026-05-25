"""
app/routes/eligibility.py – Eligibility questions and validation routes.
Handles eligibility questions for job applications, validation, and answers.
"""

from flask import Blueprint, render_template, redirect, url_for, session, jsonify, request
from ..extensions import db
from ..models import (
    Seeker, JobListing, EligibilityQuestion, EligibilityAnswer,
    JobRequirements
)
from ..services import EligibilityService

eligibility_bp = Blueprint('eligibility', __name__)


def _current_user():
    """Return (user_id, user_type) for the logged-in user, or (None, None)."""
    if session.get('seeker_id'):
        return session['seeker_id'], 'seeker'
    if session.get('company_id'):
        return session['company_id'], 'company'
    return None, None


# ═══════════════════════════════════════════════════════════════════════════
# PAGE ROUTES
# ═══════════════════════════════════════════════════════════════════════════

@eligibility_bp.route('/job/<int:job_id>/eligibility')
def eligibility_form(job_id):
    """Display eligibility form before job application"""
    seeker_id, user_type = _current_user()
    
    if user_type != 'seeker' or not seeker_id:
        return redirect(url_for('auth.login_seeker'))

    job = JobListing.query.get(job_id)
    if not job:
        return redirect(url_for('jobs.browse_jobs'))

    questions = EligibilityService.get_eligible_questions(job_id)
    seeker = Seeker.query.get(seeker_id)

    # Get job requirements
    requirements = EligibilityService.get_job_requirements(job_id)

    return render_template(
        'eligibility_form.html',
        job=job,
        questions=questions,
        seeker=seeker,
        requirements=requirements,
        job_id=job_id,
    )


# ═══════════════════════════════════════════════════════════════════════════
# API ROUTES: Eligibility Questions
# ═══════════════════════════════════════════════════════════════════════════

@eligibility_bp.route('/api/eligibility/questions/<int:job_id>', methods=['GET'])
def api_get_questions(job_id):
    """Get eligibility questions for a job"""
    questions = EligibilityService.get_eligible_questions(job_id)

    return jsonify({
        'success': True,
        'questions': [q.to_dict() for q in questions],
    }), 200


@eligibility_bp.route('/api/eligibility/all-questions', methods=['GET'])
def api_get_all_questions():
    """Get all available eligibility questions"""
    questions = EligibilityQuestion.query.filter_by(is_active=True).order_by(
        EligibilityQuestion.display_order
    ).all()

    return jsonify({
        'success': True,
        'questions': [q.to_dict() for q in questions],
    }), 200


# ═══════════════════════════════════════════════════════════════════════════
# API ROUTES: Eligibility Answers
# ═══════════════════════════════════════════════════════════════════════════

@eligibility_bp.route('/api/eligibility/answers/<int:job_id>', methods=['GET'])
def api_get_answers(job_id):
    """Get seeker's answers for a job"""
    seeker_id, user_type = _current_user()

    if user_type != 'seeker' or not seeker_id:
        return jsonify({'error': 'Unauthorized'}), 401

    answers = EligibilityService.get_seeker_answers(seeker_id, job_id)

    return jsonify({
        'success': True,
        'answers': answers,
    }), 200


@eligibility_bp.route('/api/eligibility/answer', methods=['POST'])
def api_save_answer():
    """Save a single eligibility answer"""
    seeker_id, user_type = _current_user()

    if user_type != 'seeker' or not seeker_id:
        return jsonify({'error': 'Unauthorized'}), 401

    data = request.get_json()

    required_fields = ['question_id', 'job_id', 'answer_value']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400

    answer = EligibilityService.save_eligibility_answer(
        seeker_id=seeker_id,
        question_id=data['question_id'],
        job_id=data['job_id'],
        answer_value=data['answer_value'],
    )

    if answer:
        return jsonify({
            'success': True,
            'answer': answer.to_dict(),
        }), 201
    else:
        return jsonify({'error': 'Failed to save answer'}), 500


@eligibility_bp.route('/api/eligibility/answers/bulk', methods=['POST'])
def api_save_bulk_answers():
    """Save multiple eligibility answers at once"""
    seeker_id, user_type = _current_user()

    if user_type != 'seeker' or not seeker_id:
        return jsonify({'error': 'Unauthorized'}), 401

    data = request.get_json()

    if not data or 'answers' not in data or 'job_id' not in data:
        return jsonify({'error': 'Missing required fields'}), 400

    success, errors = EligibilityService.save_bulk_answers(
        seeker_id=seeker_id,
        job_id=data['job_id'],
        answers=data['answers'],  # Dict of {question_id: answer_value}
    )

    if success:
        return jsonify({
            'success': True,
            'message': 'All answers saved successfully',
        }), 201
    else:
        return jsonify({
            'success': False,
            'errors': errors,
        }), 400


# ═══════════════════════════════════════════════════════════════════════════
# API ROUTES: Eligibility Validation
# ═══════════════════════════════════════════════════════════════════════════

@eligibility_bp.route('/api/eligibility/validate/<int:job_id>', methods=['GET'])
def api_validate_eligibility(job_id):
    """Check if seeker is eligible for a job"""
    seeker_id, user_type = _current_user()

    if user_type != 'seeker' or not seeker_id:
        return jsonify({'error': 'Unauthorized'}), 401

    is_eligible, errors = EligibilityService.validate_seeker_eligibility(
        seeker_id, job_id
    )

    return jsonify({
        'success': True,
        'is_eligible': is_eligible,
        'errors': errors,
    }), 200


@eligibility_bp.route('/api/eligibility/check-age', methods=['POST'])
def api_check_age():
    """Check age eligibility"""
    data = request.get_json()

    if not data or 'dob' not in data:
        return jsonify({'error': 'Missing date of birth'}), 400

    is_eligible, message = EligibilityService.check_age_eligibility(
        dob=data['dob'],
        min_age=data.get('min_age'),
        max_age=data.get('max_age'),
    )

    return jsonify({
        'success': True,
        'is_eligible': is_eligible,
        'message': message,
    }), 200


@eligibility_bp.route('/api/eligibility/check-work-auth', methods=['POST'])
def api_check_work_auth():
    """Check work authorization eligibility"""
    data = request.get_json()

    if not data or 'work_auth' not in data:
        return jsonify({'error': 'Missing work authorization'}), 400

    is_eligible, message = EligibilityService.check_work_auth_eligibility(
        seeker_work_auth=data['work_auth'],
        allowed_work_auth=data.get('allowed_work_auth', ''),
    )

    return jsonify({
        'success': True,
        'is_eligible': is_eligible,
        'message': message,
    }), 200


# ═══════════════════════════════════════════════════════════════════════════
# API ROUTES: Job Requirements Management (for companies)
# ═══════════════════════════════════════════════════════════════════════════

@eligibility_bp.route('/api/job-requirements/<int:job_id>', methods=['GET'])
def api_get_job_requirements(job_id):
    """Get job requirements"""
    requirements = EligibilityService.get_job_requirements(job_id)

    if requirements:
        return jsonify({
            'success': True,
            'requirements': requirements.to_dict(),
        }), 200
    else:
        return jsonify({
            'success': True,
            'requirements': None,
        }), 200


@eligibility_bp.route('/api/job-requirements/<int:job_id>', methods=['POST'])
def api_create_job_requirements(job_id):
    """Create or update job requirements"""
    company_id, user_type = _current_user()

    if user_type != 'company' or not company_id:
        return jsonify({'error': 'Unauthorized'}), 401

    # Verify company owns this job
    job = JobListing.query.get(job_id)
    if not job or job.company_id != company_id:
        return jsonify({'error': 'Not authorized to modify this job'}), 403

    data = request.get_json()

    success = EligibilityService.update_job_requirements(job_id, **data)

    if success:
        requirements = EligibilityService.get_job_requirements(job_id)
        return jsonify({
            'success': True,
            'message': 'Job requirements updated',
            'requirements': requirements.to_dict(),
        }), 200
    else:
        return jsonify({'error': 'Failed to update job requirements'}), 500


# ═══════════════════════════════════════════════════════════════════════════
# API ROUTES: Admin - Initialize Questions
# ═══════════════════════════════════════════════════════════════════════════

@eligibility_bp.route('/api/admin/initialize-questions', methods=['POST'])
def api_initialize_questions():
    """
    Initialize default eligibility questions.
    Should be restricted to admin users only in production.
    """
    # TODO: Add admin authentication check
    
    success = EligibilityService.create_eligibility_questions()

    if success:
        return jsonify({
            'success': True,
            'message': 'Default eligibility questions initialized',
        }), 201
    else:
        return jsonify({'error': 'Failed to initialize questions'}), 500
