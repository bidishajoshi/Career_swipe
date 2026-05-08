"""Employer model - Represents companies posting jobs"""

from extensions import db
from datetime import datetime


class Employer(db.Model):
    """
    Employer model represents companies in the CareerSwipe platform.
    Stores company profile information and manages job postings.
    """
    __tablename__ = 'employers'
    
    # Primary Key
    id = db.Column(db.Integer, primary_key=True)
    
    # Company Information
    company_name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), nullable=False, unique=True, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.String(30))
    company_address = db.Column(db.String(500))
    industry = db.Column(db.String(150))
    
    # Account Status
    verification_token = db.Column(db.String(100))
    is_verified = db.Column(db.Boolean, default=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    jobs = db.relationship(
        'Job',
        backref='employer',
        lazy=True,
        cascade='all, delete-orphan'
    )
    
    def to_dict(self):
        """Convert Employer object to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'company_name': self.company_name,
            'email': self.email,
            'phone': self.phone,
            'company_address': self.company_address,
            'industry': self.industry,
            'is_verified': self.is_verified,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f"<Employer {self.company_name}>"
