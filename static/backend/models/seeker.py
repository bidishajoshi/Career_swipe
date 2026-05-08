"""Seeker model - Represents job seekers/candidates"""

from extensions import db
from datetime import datetime


class Seeker(db.Model):
    """
    Seeker model represents job seekers in the CareerSwipe platform.
    Stores candidate profile information, resume data, and job preferences.
    """
    __tablename__ = 'seekers'
    
    # Primary Key
    id = db.Column(db.Integer, primary_key=True)
    
    # Personal Information
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(255), nullable=False, unique=True, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.String(30))
    address = db.Column(db.String(500))
    
    # Professional Information
    education = db.Column(db.String(255))
    experience = db.Column(db.Text)                    # Work experience description
    skills = db.Column(db.Text)                        # Comma-separated or JSON
    resume_path = db.Column(db.String(500))            # Path to uploaded resume file
    
    # Additional Profile Fields
    gender = db.Column(db.String(20))
    dob = db.Column(db.String(20))
    
    # Job Preferences
    experience_type = db.Column(db.String(50))         # fresher / experienced
    career_field = db.Column(db.String(100))           # IT / Marketing / Finance etc
    job_status = db.Column(db.String(50))              # searching / employed / open to offers
    job_location_type = db.Column(db.String(50))       # remote / onsite / hybrid
    shift_preference = db.Column(db.String(50))        # day / night / flexible
    
    desired_roles = db.Column(db.String(255))
    salary_expectation = db.Column(db.String(100))
    availability = db.Column(db.String(100))
    
    # Account Status
    verification_token = db.Column(db.String(100))
    is_verified = db.Column(db.Boolean, default=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    applications = db.relationship(
        'Application',
        backref='seeker',
        lazy=True,
        cascade='all, delete-orphan'
    )
    
    def to_dict(self):
        """Convert Seeker object to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'email': self.email,
            'phone': self.phone,
            'address': self.address,
            'education': self.education,
            'experience': self.experience,
            'skills': self.skills,
            'resume_path': self.resume_path,
            'gender': self.gender,
            'dob': self.dob,
            'experience_type': self.experience_type,
            'career_field': self.career_field,
            'job_status': self.job_status,
            'job_location_type': self.job_location_type,
            'shift_preference': self.shift_preference,
            'desired_roles': self.desired_roles,
            'salary_expectation': self.salary_expectation,
            'availability': self.availability,
            'is_verified': self.is_verified,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f"<Seeker {self.email}>"
