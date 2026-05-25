"""
app/models/__init__.py – Re-exports all models for convenient imports.
Usage: from app.models import Seeker, Company, JobListing, JobSwipe, Notification, etc.
"""

from .seeker import Seeker
from .company import Company
from .job_listing import JobListing
from .job_swipe import JobSwipe
from .notification import Notification
from .eligibility_question import EligibilityQuestion
from .eligibility_answer import EligibilityAnswer
from .job_requirements import JobRequirements
from .interview_invite import InterviewInvite
from .notification_preference import NotificationPreference

__all__ = [
    'Seeker', 'Company', 'JobListing', 'JobSwipe', 'Notification',
    'EligibilityQuestion', 'EligibilityAnswer', 'JobRequirements',
    'InterviewInvite', 'NotificationPreference'
]
