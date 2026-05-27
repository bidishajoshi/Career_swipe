"""
app/models/job_requirements.py – Job-specific eligibility requirements.
Table: job_requirements
"""

from datetime import datetime
from ..extensions import db


class JobRequirements(db.Model):
    __tablename__ = 'job_requirements'

    id                   = db.Column(db.Integer, primary_key=True)
    job_id               = db.Column(db.Integer, db.ForeignKey('jobs.id', ondelete='CASCADE'), nullable=False, unique=True, index=True)
    
    # Age requirements
    min_age              = db.Column(db.Integer)
    max_age              = db.Column(db.Integer)
    
    # Experience requirements (years)
    min_years_experience = db.Column(db.Integer, default=0)
    max_years_experience = db.Column(db.Integer)
    
    # Work authorization/eligibility (stored as comma-separated values)
    # Options: citizen, permanent_resident, visa_sponsored, remote_international
    allowed_work_auth    = db.Column(db.Text)
    
    # Availability requirements
    required_availability = db.Column(db.String(100))  # full_time, part_time, flexible
    
    # Relocation requirement
    relocation_required  = db.Column(db.Boolean, default=False)
    
    # Salary expectations (optional)
    min_salary           = db.Column(db.Integer)
    max_salary           = db.Column(db.Integer)
    
    # Notice period (days)
    required_notice_period = db.Column(db.Integer)  # in days, e.g., 30, 60
    
    # Required skills (comma-separated or JSON)
    required_skills      = db.Column(db.Text)
    
    # Legal eligibility required
    legally_eligible_required = db.Column(db.Boolean, default=True)
    
    # Custom requirements (JSON)
    custom_requirements  = db.Column(db.Text)  # For any custom validation rules
    
    # Metadata
    created_at           = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at           = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship
    job = db.relationship('JobListing', backref='requirements')

    def to_dict(self):
        import json
        return {
            'id': self.id,
            'job_id': self.job_id,
            'min_age': self.min_age,
            'max_age': self.max_age,
            'min_years_experience': self.min_years_experience,
            'max_years_experience': self.max_years_experience,
            'allowed_work_auth': self.allowed_work_auth.split(',') if self.allowed_work_auth else [],
            'required_availability': self.required_availability,
            'relocation_required': self.relocation_required,
            'min_salary': self.min_salary,
            'max_salary': self.max_salary,
            'required_notice_period': self.required_notice_period,
            'required_skills': self.required_skills,
            'legally_eligible_required': self.legally_eligible_required,
            'custom_requirements': json.loads(self.custom_requirements) if self.custom_requirements else {},
        }
