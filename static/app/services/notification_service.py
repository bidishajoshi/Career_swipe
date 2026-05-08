"""
app/services/notification_service.py – In-app notification helper.
Keeps notification creation logic out of route handlers.
"""

from ..extensions import db
from ..models.notification import Notification


def create_notification(
    user_id: int,
    user_type: str,
    message: str,
    type: str = 'system',
) -> bool:
    """
    Persist an in-app notification record.

    Args:
        user_id:   ID of the target user (seeker or company).
        user_type: 'seeker' or 'company'.
        message:   Notification body text.
        type:      Category tag (application / accepted / rejected / interview / system).

    Returns:
        True on success, False on failure.
    """
    try:
        notif = Notification(
            user_id=user_id,
            user_type=user_type,
            message=message,
            type=type,
        )
        db.session.add(notif)
        db.session.commit()
        return True
    except Exception as e:
        print(f'[notification_service] Error creating notification: {e}')
        db.session.rollback()
        return False
