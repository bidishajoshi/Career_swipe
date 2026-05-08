"""Application Controller - Handles job applications"""

from extensions import db
from backend.models import Application, Job, Seeker, Employer, Notification
from datetime import datetime
from sqlalchemy.exc import IntegrityError


class ApplicationController:
    """Controller for job application operations"""
    
    @staticmethod
    def apply_to_job(seeker_id, job_id):
        """
        Create a new job application
        
        Args:
            seeker_id (int): ID of the seeker applying
            job_id (int): ID of the job
        
        Returns:
            dict: Response with status, message, and application_id if successful
        """
        try:
            # Validate seeker exists
            seeker = Seeker.query.get(seeker_id)
            if not seeker:
                return {
                    'success': False,
                    'message': 'Seeker not found'
                }
            
            # Validate job exists
            job = Job.query.get(job_id)
            if not job:
                return {
                    'success': False,
                    'message': 'Job not found'
                }
            
            # Check if already applied
            existing_app = Application.query.filter_by(
                seeker_id=seeker_id,
                job_id=job_id
            ).first()
            
            if existing_app:
                return {
                    'success': False,
                    'message': 'You have already applied to this job'
                }
            
            # Create new application
            application = Application(
                seeker_id=seeker_id,
                job_id=job_id,
                status='pending'
            )
            
            db.session.add(application)
            db.session.commit()
            
            # Create notification for employer
            employer = Employer.query.get(job.employer_id)
            if employer:
                notification = Notification(
                    user_id=employer.id,
                    user_type='employer',
                    message=f'{seeker.first_name} {seeker.last_name} applied for {job.title}',
                    type='application'
                )
                db.session.add(notification)
                db.session.commit()
            
            return {
                'success': True,
                'message': 'Application submitted successfully',
                'application_id': application.id
            }
        
        except IntegrityError:
            db.session.rollback()
            return {
                'success': False,
                'message': 'You have already applied to this job'
            }
        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'message': f'Application error: {str(e)}'
            }
    
    @staticmethod
    def get_seeker_applications(seeker_id, limit=20, offset=0):
        """
        Get all applications from a seeker
        
        Args:
            seeker_id (int): Seeker ID
            limit (int): Number of applications to return
            offset (int): Number of applications to skip
        
        Returns:
            dict: Response with status, message, and applications list
        """
        try:
            # Validate seeker exists
            seeker = Seeker.query.get(seeker_id)
            if not seeker:
                return {
                    'success': False,
                    'message': 'Seeker not found'
                }
            
            applications = Application.query.filter_by(seeker_id=seeker_id)\
                .order_by(Application.applied_at.desc())\
                .limit(limit)\
                .offset(offset)\
                .all()
            
            total = Application.query.filter_by(seeker_id=seeker_id).count()
            
            apps_data = []
            for app in applications:
                app_dict = app.to_dict()
                job = Job.query.get(app.job_id)
                if job:
                    app_dict['job'] = job.to_dict()
                apps_data.append(app_dict)
            
            return {
                'success': True,
                'applications': apps_data,
                'total': total,
                'limit': limit,
                'offset': offset
            }
        
        except Exception as e:
            return {
                'success': False,
                'message': f'Error fetching applications: {str(e)}'
            }
    
    @staticmethod
    def get_job_applications(job_id, employer_id, limit=20, offset=0):
        """
        Get all applications for a specific job
        
        Args:
            job_id (int): Job ID
            employer_id (int): Employer ID (to verify ownership)
            limit (int): Number of applications to return
            offset (int): Number of applications to skip
        
        Returns:
            dict: Response with status, message, and applications list
        """
        try:
            # Validate job exists and employer owns it
            job = Job.query.get(job_id)
            if not job:
                return {
                    'success': False,
                    'message': 'Job not found'
                }
            
            if job.employer_id != employer_id:
                return {
                    'success': False,
                    'message': 'Unauthorized - not the job owner'
                }
            
            applications = Application.query.filter_by(job_id=job_id)\
                .order_by(Application.applied_at.desc())\
                .limit(limit)\
                .offset(offset)\
                .all()
            
            total = Application.query.filter_by(job_id=job_id).count()
            
            apps_data = []
            for app in applications:
                app_dict = app.to_dict()
                seeker = Seeker.query.get(app.seeker_id)
                if seeker:
                    app_dict['seeker'] = seeker.to_dict()
                apps_data.append(app_dict)
            
            return {
                'success': True,
                'applications': apps_data,
                'total': total,
                'limit': limit,
                'offset': offset
            }
        
        except Exception as e:
            return {
                'success': False,
                'message': f'Error fetching applications: {str(e)}'
            }
    
    @staticmethod
    def update_application_status(application_id, job_id, employer_id, new_status):
        """
        Update application status (by employer)
        
        Args:
            application_id (int): Application ID
            job_id (int): Job ID (to verify ownership)
            employer_id (int): Employer ID (to verify ownership)
            new_status (str): New status
        
        Returns:
            dict: Response with status and message
        """
        try:
            # Validate application exists
            application = Application.query.get(application_id)
            if not application:
                return {
                    'success': False,
                    'message': 'Application not found'
                }
            
            # Validate job and employer ownership
            job = Job.query.get(job_id)
            if not job or job.employer_id != employer_id:
                return {
                    'success': False,
                    'message': 'Unauthorized - not the job owner'
                }
            
            # Verify application is for this job
            if application.job_id != job_id:
                return {
                    'success': False,
                    'message': 'Application does not belong to this job'
                }
            
            # Update status
            valid_statuses = ['pending', 'shortlisted', 'rejected', 'interview', 'accepted']
            if new_status not in valid_statuses:
                return {
                    'success': False,
                    'message': f'Invalid status. Must be one of: {", ".join(valid_statuses)}'
                }
            
            application.status = new_status
            application.updated_at = datetime.utcnow()
            db.session.commit()
            
            # Create notification for seeker
            seeker = Seeker.query.get(application.seeker_id)
            if seeker:
                status_messages = {
                    'shortlisted': f'Great! You have been shortlisted for {job.title}',
                    'rejected': f'Your application for {job.title} has been reviewed',
                    'interview': f'You have been invited for an interview for {job.title}',
                    'accepted': f'Congratulations! Your application for {job.title} has been accepted'
                }
                
                if new_status in status_messages:
                    notification = Notification(
                        user_id=seeker.id,
                        user_type='seeker',
                        message=status_messages[new_status],
                        type=new_status
                    )
                    db.session.add(notification)
                    db.session.commit()
            
            return {
                'success': True,
                'message': f'Application status updated to {new_status}'
            }
        
        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'message': f'Error updating application: {str(e)}'
            }
    
    @staticmethod
    def get_application_by_id(application_id, user_id, user_type):
        """
        Get a specific application (accessible by seeker or employer who owns it)
        
        Args:
            application_id (int): Application ID
            user_id (int): User ID requesting
            user_type (str): 'seeker' or 'employer'
        
        Returns:
            dict: Response with status, message, and application data
        """
        try:
            application = Application.query.get(application_id)
            
            if not application:
                return {
                    'success': False,
                    'message': 'Application not found'
                }
            
            # Check authorization
            if user_type == 'seeker':
                if application.seeker_id != user_id:
                    return {
                        'success': False,
                        'message': 'Unauthorized - not your application'
                    }
            elif user_type == 'employer':
                job = Job.query.get(application.job_id)
                if not job or job.employer_id != user_id:
                    return {
                        'success': False,
                        'message': 'Unauthorized - not your job'
                    }
            else:
                return {
                    'success': False,
                    'message': 'Invalid user type'
                }
            
            app_dict = application.to_dict()
            
            # Include related data
            job = Job.query.get(application.job_id)
            if job:
                app_dict['job'] = job.to_dict()
            
            seeker = Seeker.query.get(application.seeker_id)
            if seeker:
                app_dict['seeker'] = seeker.to_dict()
            
            return {
                'success': True,
                'application': app_dict
            }
        
        except Exception as e:
            return {
                'success': False,
                'message': f'Error fetching application: {str(e)}'
            }
