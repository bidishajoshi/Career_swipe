"""
app/models/notification.py – In-app notification model.
Table: notifications
"""

from datetime import datetime
from ..extensions import db


class Notification(db.Model):
    __tablename__ = 'app_notifications'

    id                   = db.Column(db.Integer, primary_key=True)
    
    # Recipient (seeker or company)
    recipient_id         = db.Column(db.Integer, nullable=False, index=True)
    recipient_type       = db.Column(db.String(20), nullable=False, index=True)  # 'seeker' or 'company'
    
    # Notification content
    title                = db.Column(db.String(255), nullable=False)
    message              = db.Column(db.Text, nullable=False)
    
    # Notification type for categorization
    notification_type    = db.Column(db.String(50), nullable=False, index=True)
    # Types: app_submitted, app_accepted, app_rejected, interview_invite, 
    #        profile_updated, new_job_match, message_received, status_changed, 
    #        withdrawal_confirmed, job_expired, interview_response

    # Related objects for linking
    related_job_id       = db.Column(db.Integer, db.ForeignKey('jobs.id', ondelete='SET NULL'), nullable=True)
    related_seeker_id    = db.Column(db.Integer, db.ForeignKey('seekers.id', ondelete='SET NULL'), nullable=True)
    related_application_id = db.Column(db.Integer, db.ForeignKey('applications.id', ondelete='SET NULL'), nullable=True)
    related_company_id   = db.Column(db.Integer, db.ForeignKey('employers.id', ondelete='SET NULL'), nullable=True)
    
    # Metadata
    is_read              = db.Column(db.Boolean, default=False, index=True)
    is_deleted           = db.Column(db.Boolean, default=False)
    is_archived          = db.Column(db.Boolean, default=False)
    action_url           = db.Column(db.String(500))  # e.g., "/job/123" or "/application/456"
    
    # Timestamps
    created_at           = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    read_at              = db.Column(db.DateTime, nullable=True)
    archived_at          = db.Column(db.DateTime, nullable=True)
    updated_at           = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id':                    self.id,
            'title':                 self.title,
            'message':               self.message,
            'notification_type':     self.notification_type,
            'type':                  self.notification_type,
            'user_id':               self.recipient_id,
            'user_type':             self.recipient_type,
            'is_read':               self.is_read,
            'is_deleted':            self.is_deleted,
            'is_archived':           self.is_archived,
            'action_url':            self.action_url,
            'related_job_id':        self.related_job_id,
            'related_seeker_id':     self.related_seeker_id,
            'related_application_id': self.related_application_id,
            'created_at':            self.created_at.isoformat() if self.created_at else None,
            'read_at':               self.read_at.isoformat() if self.read_at else None,
        }

    @property
    def type(self):
        return self.notification_type

    @property
    def user_id(self):
        return self.recipient_id

    @property
    def user_type(self):
        return self.recipient_type
    
    def mark_as_read(self):
        """Mark notification as read"""
        self.is_read = True
        self.read_at = datetime.utcnow()
    
    def archive(self):
        """Archive notification"""
        self.is_archived = True
        self.archived_at = datetime.utcnow()
