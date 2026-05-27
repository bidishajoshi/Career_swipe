"""
app/models/notification_preference.py – User notification preferences.
Table: notification_preferences
"""

from datetime import datetime
from ..extensions import db


class NotificationPreference(db.Model):
    __tablename__ = 'notification_preferences'

    id                   = db.Column(db.Integer, primary_key=True)
    
    # User reference
    user_id              = db.Column(db.Integer, nullable=False, index=True)
    user_type            = db.Column(db.String(20), nullable=False, index=True)  # 'seeker' or 'company'
    
    # Seeker notification preferences
    notify_app_accepted  = db.Column(db.Boolean, default=True)
    notify_app_rejected  = db.Column(db.Boolean, default=True)
    notify_interview     = db.Column(db.Boolean, default=True)
    notify_new_jobs      = db.Column(db.Boolean, default=True)
    notify_messages      = db.Column(db.Boolean, default=True)
    notify_profile_views = db.Column(db.Boolean, default=True)
    notify_app_updates   = db.Column(db.Boolean, default=True)
    
    # Company notification preferences
    notify_new_applications = db.Column(db.Boolean, default=True)
    notify_seeker_updates   = db.Column(db.Boolean, default=True)
    notify_interview_responses = db.Column(db.Boolean, default=True)
    notify_job_expiration   = db.Column(db.Boolean, default=True)
    notify_withdrawals      = db.Column(db.Boolean, default=True)
    notify_messages_company = db.Column(db.Boolean, default=True)
    
    # Email notification preferences
    email_enabled        = db.Column(db.Boolean, default=True)
    email_digest         = db.Column(db.String(50), default='immediate')  # immediate, daily, weekly
    
    # In-app notification preferences
    in_app_enabled       = db.Column(db.Boolean, default=True)
    
    # Notification quiet hours (e.g., no notifications between 10 PM - 8 AM)
    quiet_hours_enabled  = db.Column(db.Boolean, default=False)
    quiet_hours_start    = db.Column(db.String(5))  # HH:MM format
    quiet_hours_end      = db.Column(db.String(5))  # HH:MM format
    
    # Metadata
    created_at           = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at           = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Unique constraint
    __table_args__       = (db.UniqueConstraint('user_id', 'user_type', name='unique_user_preferences'),)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'user_type': self.user_type,
            'notify_app_accepted': self.notify_app_accepted,
            'notify_app_rejected': self.notify_app_rejected,
            'notify_interview': self.notify_interview,
            'notify_new_jobs': self.notify_new_jobs,
            'notify_messages': self.notify_messages,
            'email_enabled': self.email_enabled,
            'email_digest': self.email_digest,
            'in_app_enabled': self.in_app_enabled,
            'quiet_hours_enabled': self.quiet_hours_enabled,
            'quiet_hours_start': self.quiet_hours_start,
            'quiet_hours_end': self.quiet_hours_end,
        }
