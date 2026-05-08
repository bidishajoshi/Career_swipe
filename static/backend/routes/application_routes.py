"""Application API Routes"""

from flask import request, jsonify
from backend.routes import application_bp
from backend.controllers import ApplicationController


@application_bp.route('', methods=['POST'])
def apply_to_job():
    """
    Apply to a job
    
    Request JSON:
    {
        "seeker_id": 1,
        "job_id": 1
    }
    
    Returns:
    {
        "success": true,
        "message": "Application submitted successfully",
        "application_id": 1
    }
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'message': 'No JSON data provided'
            }), 400
        
        seeker_id = data.get('seeker_id')
        job_id = data.get('job_id')
        
        if not seeker_id or not job_id:
            return jsonify({
                'success': False,
                'message': 'seeker_id and job_id are required'
            }), 400
        
        result = ApplicationController.apply_to_job(seeker_id, job_id)
        status_code = 201 if result['success'] else 400
        
        return jsonify(result), status_code
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Server error: {str(e)}'
        }), 500


@application_bp.route('/seeker/<int:seeker_id>', methods=['GET'])
def get_seeker_applications(seeker_id):
    """
    Get all applications from a seeker
    
    Query Parameters:
    - limit: Number of applications to return (default: 20)
    - offset: Number of applications to skip (default: 0)
    
    Returns:
    {
        "success": true,
        "applications": [ ... applications with job data ... ],
        "total": 5,
        "limit": 20,
        "offset": 0
    }
    """
    try:
        limit = request.args.get('limit', 20, type=int)
        offset = request.args.get('offset', 0, type=int)
        
        # Validate pagination parameters
        if limit > 100:
            limit = 100
        if limit < 1:
            limit = 1
        if offset < 0:
            offset = 0
        
        result = ApplicationController.get_seeker_applications(seeker_id, limit, offset)
        status_code = 200 if result['success'] else 404
        
        return jsonify(result), status_code
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Server error: {str(e)}'
        }), 500


@application_bp.route('/job/<int:job_id>', methods=['GET'])
def get_job_applications(job_id):
    """
    Get all applications for a specific job (employer only)
    
    Query Parameters:
    - employer_id: Employer ID (required for authorization)
    - limit: Number of applications to return (default: 20)
    - offset: Number of applications to skip (default: 0)
    
    Returns:
    {
        "success": true,
        "applications": [ ... applications with seeker data ... ],
        "total": 10,
        "limit": 20,
        "offset": 0
    }
    """
    try:
        employer_id = request.args.get('employer_id', type=int)
        limit = request.args.get('limit', 20, type=int)
        offset = request.args.get('offset', 0, type=int)
        
        if not employer_id:
            return jsonify({
                'success': False,
                'message': 'employer_id is required'
            }), 400
        
        # Validate pagination parameters
        if limit > 100:
            limit = 100
        if limit < 1:
            limit = 1
        if offset < 0:
            offset = 0
        
        result = ApplicationController.get_job_applications(job_id, employer_id, limit, offset)
        status_code = 200 if result['success'] else 400
        
        return jsonify(result), status_code
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Server error: {str(e)}'
        }), 500


@application_bp.route('/<int:application_id>/status', methods=['PUT'])
def update_application_status(application_id):
    """
    Update application status (employer only)
    
    Request JSON:
    {
        "employer_id": 1,
        "job_id": 1,
        "status": "shortlisted"
    }
    
    Valid statuses: pending, shortlisted, rejected, interview, accepted
    
    Returns:
    {
        "success": true,
        "message": "Application status updated to shortlisted"
    }
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'message': 'No JSON data provided'
            }), 400
        
        employer_id = data.get('employer_id')
        job_id = data.get('job_id')
        new_status = data.get('status')
        
        if not employer_id or not job_id or not new_status:
            return jsonify({
                'success': False,
                'message': 'employer_id, job_id, and status are required'
            }), 400
        
        result = ApplicationController.update_application_status(
            application_id, job_id, employer_id, new_status
        )
        status_code = 200 if result['success'] else 400
        
        return jsonify(result), status_code
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Server error: {str(e)}'
        }), 500


@application_bp.route('/<int:application_id>', methods=['GET'])
def get_application(application_id):
    """
    Get a specific application
    
    Query Parameters:
    - user_id: User ID requesting (required)
    - user_type: 'seeker' or 'employer' (required)
    
    Returns:
    {
        "success": true,
        "application": { ... application with job and seeker data ... }
    }
    """
    try:
        user_id = request.args.get('user_id', type=int)
        user_type = request.args.get('user_type')
        
        if not user_id or not user_type:
            return jsonify({
                'success': False,
                'message': 'user_id and user_type are required'
            }), 400
        
        result = ApplicationController.get_application_by_id(application_id, user_id, user_type)
        status_code = 200 if result['success'] else 400
        
        return jsonify(result), status_code
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Server error: {str(e)}'
        }), 500
