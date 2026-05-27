"""
app/models/job_listing.py – Job posting model.
Table: jobs (renamed from job_listings in migration 001_full_schema)
"""

from datetime import datetime
from ..extensions import db


class JobListing(db.Model):
    """
    Job posting by a company/employer.
    Table name: 'jobs' (renamed for clarity).
    Class kept as 'JobListing' for backwards compatibility with routes.
    """
    __tablename__ = 'jobs'

    id                   = db.Column(db.Integer, primary_key=True)
    company_id           = db.Column(
        db.Integer,
        db.ForeignKey('employers.id', ondelete='CASCADE'),
        nullable=False,
        index=True,
    )

    # Job details
    title                = db.Column(db.String(255), nullable=False)
    description          = db.Column(db.Text, nullable=False)
    required_skills      = db.Column(db.Text)
    location             = db.Column(db.String(255))
    job_type             = db.Column(db.String(50), default='Full-time')    # Full-time / Part-time / Contract
    job_location_type    = db.Column(db.String(50), default='Onsite')       # Onsite / Remote / Hybrid
    experience_level     = db.Column(db.String(50), default='Entry Level')  # Entry / Mid / Senior
    min_experience       = db.Column(db.Integer, default=0)                 # years
    experience_required  = db.Column(db.String(100))                        # human-readable, e.g. "2-3 years"
    salary               = db.Column(db.String(100))
    max_salary           = db.Column(db.Integer)
    tags                 = db.Column(db.Text)                                # comma-separated keywords
    is_boosted           = db.Column(db.Boolean, default=False)
    created_at           = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    swipes = db.relationship(
        'JobSwipe',
        backref='job_listing',
        lazy=True,
        cascade='all, delete-orphan',
    )

    def to_dict(self):
        return {
            'id':                 self.id,
            'employer_id':        self.company_id,
            'title':              self.title,
            'description':        self.description,
            'required_skills':    self.required_skills,
            'location':           self.location,
            'job_type':           self.job_type,
            'job_location_type':  self.job_location_type,
            'experience_level':   self.experience_level,
            'experience_required':self.experience_required,
            'salary':             self.salary,
            'is_boosted':         self.is_boosted,
            'created_at':         self.created_at.isoformat() if self.created_at else None,
        }
