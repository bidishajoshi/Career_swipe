"""
app/models/notification.py – In-app notification model.
Table: notifications
"""

from datetime import datetime
from ..extensions import db


class Notification(db.Model):
    __tablename__ = 'notifications'

    id         = db.Column(db.Integer, primary_key=True)
    user_id    = db.Column(db.Integer, nullable=False, index=True)
    user_type  = db.Column(db.String(20), nullable=False, index=True)  # 'seeker' or 'company'
    message    = db.Column(db.Text, nullable=False)
    type       = db.Column(db.String(50), default='system')            # application / accepted / rejected / interview / system
    is_read    = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id':         self.id,
            'message':    self.message,
            'type':       self.type,
            'is_read':    self.is_read,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
