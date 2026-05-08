"""Authentication Controller - Handles user registration and login"""

from extensions import db
from backend.models import Seeker, Employer
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import re


class AuthController:
    """Controller for authentication operations"""
    
    @staticmethod
    def validate_email(email):
        """Validate email format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    @staticmethod
    def validate_password(password):
        """
        Validate password strength.
        Requirements: minimum 8 characters
        """
        return len(password) >= 8
    
    @staticmethod
    def register_seeker(data):
        """
        Register a new seeker
        
        Args:
            data (dict): Registration data including:
                - first_name: str
                - last_name: str
                - email: str
                - password: str
                - phone: str (optional)
                - career_field: str (optional)
        
        Returns:
            dict: Response with status, message, and seeker_id if successful
        """
        try:
            # Validate required fields
            required_fields = ['first_name', 'last_name', 'email', 'password']
            for field in required_fields:
                if not data.get(field):
                    return {
                        'success': False,
                        'message': f'Missing required field: {field}'
                    }
            
            # Validate email format
            if not AuthController.validate_email(data['email']):
                return {
                    'success': False,
                    'message': 'Invalid email format'
                }
            
            # Check if email already exists
            if Seeker.query.filter_by(email=data['email']).first():
                return {
                    'success': False,
                    'message': 'Email already registered'
                }
            
            # Validate password strength
            if not AuthController.validate_password(data['password']):
                return {
                    'success': False,
                    'message': 'Password must be at least 8 characters long'
                }
            
            # Create new seeker
            seeker = Seeker(
                first_name=data['first_name'],
                last_name=data['last_name'],
                email=data['email'],
                password_hash=generate_password_hash(data['password']),
                phone=data.get('phone'),
                career_field=data.get('career_field'),
                experience_type=data.get('experience_type'),
                job_status=data.get('job_status', 'searching'),
                is_verified=False
            )
            
            db.session.add(seeker)
            db.session.commit()
            
            return {
                'success': True,
                'message': 'Seeker registered successfully',
                'seeker_id': seeker.id
            }
        
        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'message': f'Registration error: {str(e)}'
            }
    
    @staticmethod
    def register_employer(data):
        """
        Register a new employer
        
        Args:
            data (dict): Registration data including:
                - company_name: str
                - email: str
                - password: str
                - phone: str (optional)
                - industry: str (optional)
        
        Returns:
            dict: Response with status, message, and employer_id if successful
        """
        try:
            # Validate required fields
            required_fields = ['company_name', 'email', 'password']
            for field in required_fields:
                if not data.get(field):
                    return {
                        'success': False,
                        'message': f'Missing required field: {field}'
                    }
            
            # Validate email format
            if not AuthController.validate_email(data['email']):
                return {
                    'success': False,
                    'message': 'Invalid email format'
                }
            
            # Check if email already exists
            if Employer.query.filter_by(email=data['email']).first():
                return {
                    'success': False,
                    'message': 'Email already registered'
                }
            
            # Validate password strength
            if not AuthController.validate_password(data['password']):
                return {
                    'success': False,
                    'message': 'Password must be at least 8 characters long'
                }
            
            # Create new employer
            employer = Employer(
                company_name=data['company_name'],
                email=data['email'],
                password_hash=generate_password_hash(data['password']),
                phone=data.get('phone'),
                company_address=data.get('company_address'),
                industry=data.get('industry'),
                is_verified=False
            )
            
            db.session.add(employer)
            db.session.commit()
            
            return {
                'success': True,
                'message': 'Employer registered successfully',
                'employer_id': employer.id
            }
        
        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'message': f'Registration error: {str(e)}'
            }
    
    @staticmethod
    def login_seeker(email, password):
        """
        Authenticate a seeker
        
        Args:
            email (str): Seeker email
            password (str): Seeker password
        
        Returns:
            dict: Response with status, message, and seeker data if successful
        """
        try:
            seeker = Seeker.query.filter_by(email=email).first()
            
            if not seeker:
                return {
                    'success': False,
                    'message': 'Invalid email or password'
                }
            
            if not check_password_hash(seeker.password_hash, password):
                return {
                    'success': False,
                    'message': 'Invalid email or password'
                }
            
            return {
                'success': True,
                'message': 'Login successful',
                'seeker': seeker.to_dict()
            }
        
        except Exception as e:
            return {
                'success': False,
                'message': f'Login error: {str(e)}'
            }
    
    @staticmethod
    def login_employer(email, password):
        """
        Authenticate an employer
        
        Args:
            email (str): Employer email
            password (str): Employer password
        
        Returns:
            dict: Response with status, message, and employer data if successful
        """
        try:
            employer = Employer.query.filter_by(email=email).first()
            
            if not employer:
                return {
                    'success': False,
                    'message': 'Invalid email or password'
                }
            
            if not check_password_hash(employer.password_hash, password):
                return {
                    'success': False,
                    'message': 'Invalid email or password'
                }
            
            return {
                'success': True,
                'message': 'Login successful',
                'employer': employer.to_dict()
            }
        
        except Exception as e:
            return {
                'success': False,
                'message': f'Login error: {str(e)}'
            }
