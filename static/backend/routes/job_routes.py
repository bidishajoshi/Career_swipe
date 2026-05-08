"""Job API Routes"""

from flask import request, jsonify
from backend.routes import job_bp
from backend.controllers import JobController


@job_bp.route('', methods=['POST'])
def create_job():
    """
    Create a new job posting (employer only)
    
    Request JSON:
    {
        "employer_id": 1,
        "title": "Senior Developer",
        "description": "Looking for experienced developers...",
        "location": "New York, NY",
        "salary": "$120,000 - $150,000",
        "job_type": "Full-time",
        "experience_required": "Senior"
    }
    
    Returns:
    {
        "success": true,
        "message": "Job posted successfully",
        "job_id": 1
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
        if not employer_id:
            return jsonify({
                'success': False,
                'message': 'employer_id is required'
            }), 400
        
        result = JobController.create_job(employer_id, data)
        status_code = 201 if result['success'] else 400
        
        return jsonify(result), status_code
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Server error: {str(e)}'
        }), 500


@job_bp.route('', methods=['GET'])
def get_jobs():
    """
    Get all job listings with pagination
    
    Query Parameters:
    - limit: Number of jobs to return (default: 20)
    - offset: Number of jobs to skip (default: 0)
    
    Returns:
    {
        "success": true,
        "jobs": [ ... jobs array ... ],
        "total": 100,
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
        
        result = JobController.get_jobs(limit, offset)
        
        return jsonify(result), 200
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Server error: {str(e)}'
        }), 500


@job_bp.route('/<int:job_id>', methods=['GET'])
def get_job(job_id):
    """
    Get a specific job by ID
    
    Returns:
    {
        "success": true,
        "job": { ... job data ... }
    }
    """
    try:
        result = JobController.get_job_by_id(job_id)
        status_code = 200 if result['success'] else 404
        
        return jsonify(result), status_code
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Server error: {str(e)}'
        }), 500


@job_bp.route('/employer/<int:employer_id>', methods=['GET'])
def get_employer_jobs(employer_id):
    """
    Get all jobs posted by a specific employer
    
    Query Parameters:
    - limit: Number of jobs to return (default: 20)
    - offset: Number of jobs to skip (default: 0)
    
    Returns:
    {
        "success": true,
        "jobs": [ ... jobs array ... ],
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
        
        result = JobController.get_employer_jobs(employer_id, limit, offset)
        status_code = 200 if result['success'] else 404
        
        return jsonify(result), status_code
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Server error: {str(e)}'
        }), 500


@job_bp.route('/<int:job_id>', methods=['PUT'])
def update_job(job_id):
    """
    Update a job posting
    
    Request JSON:
    {
        "employer_id": 1,
        "title": "Updated Title",
        "description": "Updated description...",
        ...
    }
    
    Returns:
    {
        "success": true,
        "message": "Job updated successfully"
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
        if not employer_id:
            return jsonify({
                'success': False,
                'message': 'employer_id is required'
            }), 400
        
        result = JobController.update_job(job_id, employer_id, data)
        status_code = 200 if result['success'] else 400
        
        return jsonify(result), status_code
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Server error: {str(e)}'
        }), 500


@job_bp.route('/<int:job_id>', methods=['DELETE'])
def delete_job(job_id):
    """
    Delete a job posting
    
    Request JSON:
    {
        "employer_id": 1
    }
    
    Returns:
    {
        "success": true,
        "message": "Job deleted successfully"
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
        if not employer_id:
            return jsonify({
                'success': False,
                'message': 'employer_id is required'
            }), 400
        
        result = JobController.delete_job(job_id, employer_id)
        status_code = 200 if result['success'] else 400
        
        return jsonify(result), status_code
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Server error: {str(e)}'
        }), 500
