"""Job model - Represents job listings"""

from extensions import db
from datetime import datetime


class Job(db.Model):
    """
    Job model represents job listings posted by employers.
    Contains job details, requirements, and metadata.
    """
    __tablename__ = 'jobs'
    
    # Primary Key
    id = db.Column(db.Integer, primary_key=True)
    
    # Foreign Key
    employer_id = db.Column(
        db.Integer,
        db.ForeignKey('employers.id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )
    
    # Job Information
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)
    location = db.Column(db.String(255))
    salary = db.Column(db.String(100))
    
    # Job Details
    job_type = db.Column(db.String(50), default='Full-time')           # Full-time, Part-time, Contract, Internship
    experience_required = db.Column(db.String(50))                      # Entry, Mid, Senior, Expert
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    applications = db.relationship(
        'Application',
        backref='job',
        lazy=True,
        cascade='all, delete-orphan'
    )
    
    def to_dict(self):
        """Convert Job object to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'employer_id': self.employer_id,
            'title': self.title,
            'description': self.description,
            'location': self.location,
            'salary': self.salary,
            'job_type': self.job_type,
            'experience_required': self.experience_required,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f"<Job {self.title}>"
