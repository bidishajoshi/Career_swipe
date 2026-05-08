"""Application model - Represents job applications"""

from extensions import db
from datetime import datetime


class Application(db.Model):
    """
    Application model represents job applications from seekers to jobs.
    Tracks application status and timestamps.
    """
    __tablename__ = 'applications'
    
    # Primary Key
    id = db.Column(db.Integer, primary_key=True)
    
    # Foreign Keys
    seeker_id = db.Column(
        db.Integer,
        db.ForeignKey('seekers.id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )
    job_id = db.Column(
        db.Integer,
        db.ForeignKey('jobs.id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )
    
    # Application Status
    status = db.Column(
        db.String(20),
        default='pending',
        index=True
    )  # pending / shortlisted / rejected / interview / accepted
    
    # Timestamps
    applied_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Unique constraint to prevent duplicate applications
    __table_args__ = (db.UniqueConstraint('seeker_id', 'job_id', name='unique_seeker_job'),)
    
    def to_dict(self):
        """Convert Application object to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'seeker_id': self.seeker_id,
            'job_id': self.job_id,
            'status': self.status,
            'applied_at': self.applied_at.isoformat() if self.applied_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f"<Application seeker_id={self.seeker_id} job_id={self.job_id}>"
