"""
app/models/__init__.py – Re-exports all models for convenient imports.
Usage: from app.models import Seeker, Company, JobListing, JobSwipe, Notification
"""

from .seeker import Seeker
from .company import Company
from .job_listing import JobListing
from .job_swipe import JobSwipe
from .notification import Notification

__all__ = ['Seeker', 'Company', 'JobListing', 'JobSwipe', 'Notification']
