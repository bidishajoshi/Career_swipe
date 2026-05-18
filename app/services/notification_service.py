"""
app/services/notification_service.py – Professional notification service.
Handles all notification creation, retrieval, and management operations.
"""

from datetime import datetime
from typing import List, Dict, Optional
from ..extensions import db
from ..models import Notification, NotificationPreference


class NotificationService:
    """Service layer for notification operations"""

    @staticmethod
    def create_notification(
        recipient_id: int,
        recipient_type: str,
        title: str,
        message: str,
        notification_type: str,
        related_job_id: Optional[int] = None,
        related_seeker_id: Optional[int] = None,
        related_company_id: Optional[int] = None,
        related_application_id: Optional[int] = None,
        action_url: Optional[str] = None,
    ) -> Optional[Notification]:
        """
        Create a new notification.

        Args:
            recipient_id: ID of recipient (seeker or company)
            recipient_type: 'seeker' or 'company'
            title: Short notification title
            message: Full notification message
            notification_type: Type of notification (app_submitted, app_accepted, etc.)
            related_job_id: Associated job ID if applicable
            related_seeker_id: Associated seeker ID if applicable
            related_company_id: Associated company ID if applicable
            related_application_id: Associated application ID if applicable
            action_url: URL to action related to this notification

        Returns:
            Notification object or None on error
        """
        try:
            notification = Notification(
                recipient_id=recipient_id,
                recipient_type=recipient_type,
                title=title,
                message=message,
                notification_type=notification_type,
                related_job_id=related_job_id,
                related_seeker_id=related_seeker_id,
                related_company_id=related_company_id,
                related_application_id=related_application_id,
                action_url=action_url,
            )
            db.session.add(notification)
            db.session.commit()
            return notification
        except Exception as e:
            print(f'[NotificationService] Error creating notification: {e}')
            db.session.rollback()
            return None

    @staticmethod
    def get_unread_count(user_id: int, user_type: str) -> int:
        """Get count of unread notifications for a user"""
        try:
            return Notification.query.filter_by(
                recipient_id=user_id,
                recipient_type=user_type,
                is_read=False,
                is_deleted=False,
            ).count()
        except Exception as e:
            print(f'[NotificationService] Error getting unread count: {e}')
            return 0

    @staticmethod
    def get_notifications(
        user_id: int,
        user_type: str,
        limit: int = 20,
        offset: int = 0,
        include_archived: bool = False,
        unread_only: bool = False,
    ) -> List[Notification]:
        """
        Get notifications for a user.

        Args:
            user_id: User ID
            user_type: 'seeker' or 'company'
            limit: Number of notifications to return
            offset: Offset for pagination
            include_archived: Whether to include archived notifications
            unread_only: If True, only return unread notifications

        Returns:
            List of Notification objects
        """
        try:
            query = Notification.query.filter_by(
                recipient_id=user_id,
                recipient_type=user_type,
                is_deleted=False,
            )

            if not include_archived:
                query = query.filter_by(is_archived=False)

            if unread_only:
                query = query.filter_by(is_read=False)

            return query.order_by(Notification.created_at.desc()).limit(limit).offset(offset).all()
        except Exception as e:
            print(f'[NotificationService] Error getting notifications: {e}')
            return []

    @staticmethod
    def mark_as_read(notification_id: int) -> bool:
        """Mark a notification as read"""
        try:
            notification = Notification.query.get(notification_id)
            if notification:
                notification.mark_as_read()
                db.session.commit()
                return True
            return False
        except Exception as e:
            print(f'[NotificationService] Error marking as read: {e}')
            db.session.rollback()
            return False

    @staticmethod
    def mark_all_as_read(user_id: int, user_type: str) -> bool:
        """Mark all unread notifications as read for a user"""
        try:
            Notification.query.filter_by(
                recipient_id=user_id,
                recipient_type=user_type,
                is_read=False,
                is_deleted=False,
            ).update({'is_read': True, 'read_at': datetime.utcnow()})
            db.session.commit()
            return True
        except Exception as e:
            print(f'[NotificationService] Error marking all as read: {e}')
            db.session.rollback()
            return False

    @staticmethod
    def archive_notification(notification_id: int) -> bool:
        """Archive a notification"""
        try:
            notification = Notification.query.get(notification_id)
            if notification:
                notification.archive()
                db.session.commit()
                return True
            return False
        except Exception as e:
            print(f'[NotificationService] Error archiving notification: {e}')
            db.session.rollback()
            return False

    @staticmethod
    def delete_notification(notification_id: int, soft_delete: bool = True) -> bool:
        """
        Delete a notification.

        Args:
            notification_id: ID of notification to delete
            soft_delete: If True, mark as deleted; if False, hard delete

        Returns:
            True on success, False on failure
        """
        try:
            notification = Notification.query.get(notification_id)
            if not notification:
                return False

            if soft_delete:
                notification.is_deleted = True
                db.session.commit()
            else:
                db.session.delete(notification)
                db.session.commit()
            return True
        except Exception as e:
            print(f'[NotificationService] Error deleting notification: {e}')
            db.session.rollback()
            return False

    @staticmethod
    def get_preferences(user_id: int, user_type: str) -> Optional[NotificationPreference]:
        """Get notification preferences for a user"""
        try:
            return NotificationPreference.query.filter_by(
                user_id=user_id,
                user_type=user_type,
            ).first()
        except Exception as e:
            print(f'[NotificationService] Error getting preferences: {e}')
            return None

    @staticmethod
    def create_default_preferences(user_id: int, user_type: str) -> Optional[NotificationPreference]:
        """Create default notification preferences for a new user"""
        try:
            prefs = NotificationPreference(
                user_id=user_id,
                user_type=user_type,
            )
            db.session.add(prefs)
            db.session.commit()
            return prefs
        except Exception as e:
            print(f'[NotificationService] Error creating default preferences: {e}')
            db.session.rollback()
            return None

    @staticmethod
    def update_preferences(user_id: int, user_type: str, **kwargs) -> bool:
        """Update notification preferences for a user"""
        try:
            prefs = NotificationPreference.query.filter_by(
                user_id=user_id,
                user_type=user_type,
            ).first()

            if not prefs:
                prefs = NotificationService.create_default_preferences(user_id, user_type)

            if prefs:
                for key, value in kwargs.items():
                    if hasattr(prefs, key):
                        setattr(prefs, key, value)
                db.session.commit()
                return True
            return False
        except Exception as e:
            print(f'[NotificationService] Error updating preferences: {e}')
            db.session.rollback()
            return False

    @staticmethod
    def should_notify(user_id: int, user_type: str, notification_type: str) -> bool:
        """Check if user should receive notification based on preferences"""
        try:
            prefs = NotificationService.get_preferences(user_id, user_type)

            if not prefs or not prefs.in_app_enabled:
                return False

            # Map notification types to preference fields
            preference_map = {
                'app_submitted': 'notify_app_accepted',  # This could be company preference
                'app_accepted': 'notify_app_accepted',
                'app_rejected': 'notify_app_rejected',
                'interview_invite': 'notify_interview',
                'new_job_match': 'notify_new_jobs',
                'message_received': 'notify_messages',
                'profile_updated': 'notify_seeker_updates',
                'new_application': 'notify_new_applications',
            }

            pref_field = preference_map.get(notification_type)
            if pref_field and hasattr(prefs, pref_field):
                return getattr(prefs, pref_field, True)

            return True
        except Exception as e:
            print(f'[NotificationService] Error checking should_notify: {e}')
            return False
