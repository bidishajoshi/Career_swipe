"""
app/models/company.py – Employer / Company account model.
Table: employers (renamed from companies in migration 001_full_schema)
"""

from datetime import datetime
from ..extensions import db


class Company(db.Model):
    """
    Employer / Company account.
    Table name: 'employers'  (renamed from 'companies' per schema migration).
    Class kept as 'Company' so existing route code needs no changes.
    """
    __tablename__ = 'employers'

    id                 = db.Column(db.Integer, primary_key=True)
    company_name       = db.Column(db.String(255), nullable=False)
    email              = db.Column(db.String(255), nullable=False, unique=True, index=True)
    password_hash      = db.Column(db.String(255), nullable=False)

    # Company details
    phone              = db.Column(db.String(30))
    company_address    = db.Column(db.String(500))
    description        = db.Column(db.Text)
    industry           = db.Column(db.String(150))
    website            = db.Column(db.String(300))
    logo_path          = db.Column(db.String(500))

    # Account status
    verification_token = db.Column(db.String(100))
    is_verified        = db.Column(db.Boolean, default=False)
    created_at         = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    jobs = db.relationship(
        'JobListing',
        backref='company',
        lazy=True,
        cascade='all, delete-orphan',
    )

    def to_dict(self):
        return {
            'id':              self.id,
            'company_name':    self.company_name,
            'email':           self.email,
            'phone':           self.phone,
            'company_address': self.company_address,
            'industry':        self.industry,
            'website':         self.website,
            'logo_path':       self.logo_path,
            'is_verified':     self.is_verified,
            'created_at':      self.created_at.isoformat() if self.created_at else None,
        }
