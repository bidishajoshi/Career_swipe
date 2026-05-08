"""Job Controller - Handles job posting and retrieval"""

from extensions import db
from backend.models import Job, Employer
from datetime import datetime


class JobController:
    """Controller for job operations"""
    
    @staticmethod
    def create_job(employer_id, data):
        """
        Create a new job posting
        
        Args:
            employer_id (int): ID of the employer posting the job
            data (dict): Job data including:
                - title: str (required)
                - description: str (required)
                - location: str
                - salary: str
                - job_type: str
                - experience_required: str
        
        Returns:
            dict: Response with status, message, and job_id if successful
        """
        try:
            # Validate employer exists
            employer = Employer.query.get(employer_id)
            if not employer:
                return {
                    'success': False,
                    'message': 'Employer not found'
                }
            
            # Validate required fields
            required_fields = ['title', 'description']
            for field in required_fields:
                if not data.get(field):
                    return {
                        'success': False,
                        'message': f'Missing required field: {field}'
                    }
            
            # Create new job
            job = Job(
                employer_id=employer_id,
                title=data['title'],
                description=data['description'],
                location=data.get('location'),
                salary=data.get('salary'),
                job_type=data.get('job_type', 'Full-time'),
                experience_required=data.get('experience_required')
            )
            
            db.session.add(job)
            db.session.commit()
            
            return {
                'success': True,
                'message': 'Job posted successfully',
                'job_id': job.id
            }
        
        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'message': f'Job creation error: {str(e)}'
            }
    
    @staticmethod
    def get_jobs(limit=20, offset=0):
        """
        Get all jobs with pagination
        
        Args:
            limit (int): Number of jobs to return
            offset (int): Number of jobs to skip
        
        Returns:
            dict: Response with status, message, and jobs list
        """
        try:
            jobs = Job.query.order_by(Job.created_at.desc()).limit(limit).offset(offset).all()
            total = Job.query.count()
            
            jobs_data = [job.to_dict() for job in jobs]
            
            return {
                'success': True,
                'jobs': jobs_data,
                'total': total,
                'limit': limit,
                'offset': offset
            }
        
        except Exception as e:
            return {
                'success': False,
                'message': f'Error fetching jobs: {str(e)}'
            }
    
    @staticmethod
    def get_job_by_id(job_id):
        """
        Get a specific job by ID
        
        Args:
            job_id (int): Job ID
        
        Returns:
            dict: Response with status, message, and job data
        """
        try:
            job = Job.query.get(job_id)
            
            if not job:
                return {
                    'success': False,
                    'message': 'Job not found'
                }
            
            return {
                'success': True,
                'job': job.to_dict()
            }
        
        except Exception as e:
            return {
                'success': False,
                'message': f'Error fetching job: {str(e)}'
            }
    
    @staticmethod
    def get_employer_jobs(employer_id, limit=20, offset=0):
        """
        Get all jobs posted by a specific employer
        
        Args:
            employer_id (int): Employer ID
            limit (int): Number of jobs to return
            offset (int): Number of jobs to skip
        
        Returns:
            dict: Response with status, message, and jobs list
        """
        try:
            # Validate employer exists
            employer = Employer.query.get(employer_id)
            if not employer:
                return {
                    'success': False,
                    'message': 'Employer not found'
                }
            
            jobs = Job.query.filter_by(employer_id=employer_id)\
                .order_by(Job.created_at.desc())\
                .limit(limit)\
                .offset(offset)\
                .all()
            
            total = Job.query.filter_by(employer_id=employer_id).count()
            
            jobs_data = [job.to_dict() for job in jobs]
            
            return {
                'success': True,
                'jobs': jobs_data,
                'total': total,
                'limit': limit,
                'offset': offset
            }
        
        except Exception as e:
            return {
                'success': False,
                'message': f'Error fetching employer jobs: {str(e)}'
            }
    
    @staticmethod
    def update_job(job_id, employer_id, data):
        """
        Update a job posting
        
        Args:
            job_id (int): Job ID
            employer_id (int): Employer ID (to verify ownership)
            data (dict): Updated job data
        
        Returns:
            dict: Response with status and message
        """
        try:
            job = Job.query.get(job_id)
            
            if not job:
                return {
                    'success': False,
                    'message': 'Job not found'
                }
            
            # Verify ownership
            if job.employer_id != employer_id:
                return {
                    'success': False,
                    'message': 'Unauthorized - not the job owner'
                }
            
            # Update fields
            if 'title' in data:
                job.title = data['title']
            if 'description' in data:
                job.description = data['description']
            if 'location' in data:
                job.location = data['location']
            if 'salary' in data:
                job.salary = data['salary']
            if 'job_type' in data:
                job.job_type = data['job_type']
            if 'experience_required' in data:
                job.experience_required = data['experience_required']
            
            job.updated_at = datetime.utcnow()
            db.session.commit()
            
            return {
                'success': True,
                'message': 'Job updated successfully'
            }
        
        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'message': f'Error updating job: {str(e)}'
            }
    
    @staticmethod
    def delete_job(job_id, employer_id):
        """
        Delete a job posting
        
        Args:
            job_id (int): Job ID
            employer_id (int): Employer ID (to verify ownership)
        
        Returns:
            dict: Response with status and message
        """
        try:
            job = Job.query.get(job_id)
            
            if not job:
                return {
                    'success': False,
                    'message': 'Job not found'
                }
            
            # Verify ownership
            if job.employer_id != employer_id:
                return {
                    'success': False,
                    'message': 'Unauthorized - not the job owner'
                }
            
            db.session.delete(job)
            db.session.commit()
            
            return {
                'success': True,
                'message': 'Job deleted successfully'
            }
        
        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'message': f'Error deleting job: {str(e)}'
            }
