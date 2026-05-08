"""Authentication API Routes"""

from flask import request, jsonify
from backend.routes import auth_bp
from backend.controllers import AuthController


@auth_bp.route('/register/seeker', methods=['POST'])
def register_seeker():
    """
    Register a new seeker
    
    Request JSON:
    {
        "first_name": "John",
        "last_name": "Doe",
        "email": "john@example.com",
        "password": "password123",
        "phone": "555-0001",
        "career_field": "IT"
    }
    
    Returns:
    {
        "success": true,
        "message": "Seeker registered successfully",
        "seeker_id": 1
    }
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'message': 'No JSON data provided'
            }), 400
        
        result = AuthController.register_seeker(data)
        status_code = 201 if result['success'] else 400
        
        return jsonify(result), status_code
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Server error: {str(e)}'
        }), 500


@auth_bp.route('/register/employer', methods=['POST'])
def register_employer():
    """
    Register a new employer
    
    Request JSON:
    {
        "company_name": "Tech Corp",
        "email": "tech@example.com",
        "password": "password123",
        "phone": "555-1001",
        "industry": "IT"
    }
    
    Returns:
    {
        "success": true,
        "message": "Employer registered successfully",
        "employer_id": 1
    }
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'message': 'No JSON data provided'
            }), 400
        
        result = AuthController.register_employer(data)
        status_code = 201 if result['success'] else 400
        
        return jsonify(result), status_code
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Server error: {str(e)}'
        }), 500


@auth_bp.route('/login/seeker', methods=['POST'])
def login_seeker():
    """
    Login as a seeker
    
    Request JSON:
    {
        "email": "john@example.com",
        "password": "password123"
    }
    
    Returns:
    {
        "success": true,
        "message": "Login successful",
        "seeker": { ... seeker data ... }
    }
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'message': 'No JSON data provided'
            }), 400
        
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            return jsonify({
                'success': False,
                'message': 'Email and password are required'
            }), 400
        
        result = AuthController.login_seeker(email, password)
        status_code = 200 if result['success'] else 401
        
        return jsonify(result), status_code
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Server error: {str(e)}'
        }), 500


@auth_bp.route('/login/employer', methods=['POST'])
def login_employer():
    """
    Login as an employer
    
    Request JSON:
    {
        "email": "tech@example.com",
        "password": "password123"
    }
    
    Returns:
    {
        "success": true,
        "message": "Login successful",
        "employer": { ... employer data ... }
    }
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'message': 'No JSON data provided'
            }), 400
        
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            return jsonify({
                'success': False,
                'message': 'Email and password are required'
            }), 400
        
        result = AuthController.login_employer(email, password)
        status_code = 200 if result['success'] else 401
        
        return jsonify(result), status_code
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Server error: {str(e)}'
        }), 500
