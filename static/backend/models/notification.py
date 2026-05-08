"""Notification model - Represents user notifications"""

from extensions import db
from datetime import datetime


class Notification(db.Model):
    """
    Notification model represents notifications for users.
    Handles both seeker and employer notifications.
    """
    __tablename__ = 'notifications'
    
    # Primary Key
    id = db.Column(db.Integer, primary_key=True)
    
    # User Information
    user_id = db.Column(db.Integer, nullable=False, index=True)
    user_type = db.Column(db.String(20), nullable=False, index=True)  # 'seeker' or 'employer'
    
    # Notification Content
    message = db.Column(db.Text, nullable=False)
    type = db.Column(
        db.String(50),
        default='system',
        index=True
    )  # application / accepted / rejected / interview / system
    
    # Read Status
    is_read = db.Column(db.Boolean, default=False, index=True)
    
    # Timestamp
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    def to_dict(self):
        """Convert Notification object to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'user_type': self.user_type,
            'message': self.message,
            'type': self.type,
            'is_read': self.is_read,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f"<Notification user_id={self.user_id}>"
