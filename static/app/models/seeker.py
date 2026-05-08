"""
app/models/seeker.py – Job-seeker account model.
Table: seekers (PostgreSQL)
"""

from datetime import datetime
from ..extensions import db


class Seeker(db.Model):
    __tablename__ = 'seekers'

    id                 = db.Column(db.Integer, primary_key=True)

    # Core identity
    first_name         = db.Column(db.String(100), nullable=False)
    last_name          = db.Column(db.String(100), nullable=False)
    email              = db.Column(db.String(255), nullable=False, unique=True, index=True)
    password_hash      = db.Column(db.String(255), nullable=False)

    # Contact & location
    phone              = db.Column(db.String(30))
    address            = db.Column(db.String(500))

    # Professional background
    education          = db.Column(db.String(255))
    experience         = db.Column(db.Text)
    skills             = db.Column(db.Text)
    resume_path        = db.Column(db.String(500))

    # Demographics
    gender             = db.Column(db.String(20))
    dob                = db.Column(db.String(20))

    # Job preferences
    experience_type    = db.Column(db.String(50))    # fresher / experienced
    career_field       = db.Column(db.String(100))   # IT / Marketing / etc.
    job_status         = db.Column(db.String(50))    # searching / employed / open
    job_location_type  = db.Column(db.String(50))    # remote / onsite / hybrid
    shift_preference   = db.Column(db.String(50))    # day / night / flexible
    desired_roles      = db.Column(db.String(255))
    salary_expectation = db.Column(db.String(100))
    availability       = db.Column(db.String(100))

    # Account status
    verification_token = db.Column(db.String(100))
    is_verified        = db.Column(db.Boolean, default=False)
    created_at         = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    swipes = db.relationship(
        'JobSwipe',
        backref='seeker',
        lazy=True,
        cascade='all, delete-orphan',
    )

    def to_dict(self):
        """Serialise seeker to a safe JSON-friendly dict (no password hash)."""
        return {
            'id':                self.id,
            'first_name':        self.first_name,
            'last_name':         self.last_name,
            'email':             self.email,
            'phone':             self.phone,
            'address':           self.address,
            'education':         self.education,
            'skills':            self.skills,
            'career_field':      self.career_field,
            'job_status':        self.job_status,
            'job_location_type': self.job_location_type,
            'desired_roles':     self.desired_roles,
            'salary_expectation':self.salary_expectation,
            'availability':      self.availability,
            'is_verified':       self.is_verified,
            'created_at':        self.created_at.isoformat() if self.created_at else None,
        }
