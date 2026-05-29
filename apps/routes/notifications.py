"""
app/routes/notifications.py – Comprehensive notification routes and API.
Covers: notification management, preferences, real-time updates.
"""

from flask import Blueprint, render_template, redirect, url_for, session, jsonify, request
from datetime import datetime
from ..extensions import db
from ..models import Notification, NotificationPreference
from models import Notification as OldNotification
from ..services import NotificationService

notifications_bp = Blueprint('notifications', __name__)


def _current_user():
    """Return (user_id, user_type) for the logged-in user, or (None, None)."""
    if session.get('seeker_id'):
        return session['seeker_id'], 'seeker'
    if session.get('company_id'):
        return session['company_id'], 'company'
    return None, None


# ═══════════════════════════════════════════════════════════════════════════
# PAGE ROUTES
# ═══════════════════════════════════════════════════════════════════════════

@notifications_bp.route('/notifications')
def notifications_history():
    """Display notifications history page"""
    user_id, user_type = _current_user()
    if not user_id:
        return redirect(url_for('auth.index'))

    page = request.args.get('page', 1, type=int)
    per_page = 20
    offset = (page - 1) * per_page

    notifications = OldNotification.query.filter_by(
        user_id=user_id, user_type=user_type
    ).order_by(OldNotification.created_at.desc()).limit(per_page).offset(offset).all()

    unread_count = OldNotification.query.filter_by(user_id=user_id, user_type=user_type, is_read=False).count()
    
    return render_template(
        'notifications.html',
        notifications=notifications,
        user_type=user_type,
        unread_count=unread_count,
        page=page,
    )


@notifications_bp.route('/notifications/preferences')
def notification_preferences():
    """Display notification preferences page"""
    user_id, user_type = _current_user()
    if not user_id:
        return redirect(url_for('auth.index'))

    prefs = NotificationService.get_preferences(user_id, user_type)
    
    return render_template(
        'notification_preferences.html',
        preferences=prefs,
        user_type=user_type,
    )


# ═══════════════════════════════════════════════════════════════════════════
# API ROUTES: Notification Management
# ═══════════════════════════════════════════════════════════════════════════

@notifications_bp.route('/api/notifications', methods=['GET'])
def api_get_notifications():
    """Get user's notifications with pagination"""
    user_id, user_type = _current_user()
    if not user_id:
        return jsonify({'error': 'Unauthorized'}), 401

    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 20, type=int)
    unread_only = request.args.get('unread_only', False, type=bool)

    offset = (page - 1) * limit

    query = OldNotification.query.filter_by(user_id=user_id, user_type=user_type)
    if unread_only:
        query = query.filter_by(is_read=False)
    
    notifications = query.order_by(OldNotification.created_at.desc()).limit(limit).offset(offset).all()

    return jsonify({
        'success': True,
        'notifications': [n.to_dict() for n in notifications],
        'page': page,
        'limit': limit,
    }), 200


@notifications_bp.route('/api/notifications/unread-count', methods=['GET'])
def api_unread_count():
    """Get count of unread notifications"""
    user_id, user_type = _current_user()
    if not user_id:
        return jsonify({'error': 'Unauthorized'}), 401

    count = OldNotification.query.filter_by(user_id=user_id, user_type=user_type, is_read=False).count()

    return jsonify({
        'success': True,
        'count': count,
    }), 200


@notifications_bp.route('/api/notifications/<int:notification_id>/mark-read', methods=['POST'])
def api_mark_read(notification_id):
    """Mark a notification as read"""
    user_id, user_type = _current_user()
    if not user_id:
        return jsonify({'error': 'Unauthorized'}), 401

    # Verify ownership
    notification = OldNotification.query.get(notification_id)
    if not notification or notification.user_id != user_id or notification.user_type != user_type:
        return jsonify({'error': 'Notification not found'}), 404

    notification.is_read = True
    db.session.commit()
    return jsonify({
        'success': True,
        'message': 'Notification marked as read',
    }), 200


@notifications_bp.route('/api/notifications/mark-all-read', methods=['POST'])
def api_mark_all_read():
    """Mark all unread notifications as read"""
    user_id, user_type = _current_user()
    if not user_id:
        return jsonify({'error': 'Unauthorized'}), 401

    OldNotification.query.filter_by(
        user_id=user_id, user_type=user_type, is_read=False
    ).update({'is_read': True})
    db.session.commit()
    return jsonify({
        'success': True,
        'message': 'All notifications marked as read',
    }), 200


@notifications_bp.route('/api/notifications/<int:notification_id>/archive', methods=['POST'])
def api_archive_notification(notification_id):
    """Archive a notification"""
    user_id, user_type = _current_user()
    if not user_id:
        return jsonify({'error': 'Unauthorized'}), 401

    notification = OldNotification.query.get(notification_id)
    if not notification or notification.user_id != user_id or notification.user_type != user_type:
        return jsonify({'error': 'Notification not found'}), 404

    db.session.delete(notification)
    db.session.commit()
    return jsonify({
        'success': True,
        'message': 'Notification deleted',
    }), 200


@notifications_bp.route('/api/notifications/<int:notification_id>', methods=['DELETE'])
def api_delete_notification(notification_id):
    """Delete a notification"""
    user_id, user_type = _current_user()
    if not user_id:
        return jsonify({'error': 'Unauthorized'}), 401

    # Verify ownership
    notification = OldNotification.query.get(notification_id)
    if not notification or notification.user_id != user_id or notification.user_type != user_type:
        return jsonify({'error': 'Notification not found'}), 404

    db.session.delete(notification)
    db.session.commit()
    return jsonify({
        'success': True,
        'message': 'Notification deleted',
    }), 200


# ═══════════════════════════════════════════════════════════════════════════
# API ROUTES: Notification Preferences
# ═══════════════════════════════════════════════════════════════════════════

@notifications_bp.route('/api/notifications/preferences', methods=['GET'])
def api_get_preferences():
    """Get user's notification preferences"""
    user_id, user_type = _current_user()
    if not user_id:
        return jsonify({'error': 'Unauthorized'}), 401

    prefs = NotificationService.get_preferences(user_id, user_type)
    
    if not prefs:
        # Create default preferences if they don't exist
        prefs = NotificationService.create_default_preferences(user_id, user_type)

    return jsonify({
        'success': True,
        'preferences': prefs.to_dict() if prefs else {},
    }), 200


@notifications_bp.route('/api/notifications/preferences', methods=['POST'])
def api_update_preferences():
    """Update user's notification preferences"""
    user_id, user_type = _current_user()
    if not user_id:
        return jsonify({'error': 'Unauthorized'}), 401

    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400

    if NotificationService.update_preferences(user_id, user_type, **data):
        updated_prefs = NotificationService.get_preferences(user_id, user_type)
        return jsonify({
            'success': True,
            'message': 'Preferences updated',
            'preferences': updated_prefs.to_dict(),
        }), 200
    else:
        return jsonify({'error': 'Failed to update preferences'}), 500


# ═══════════════════════════════════════════════════════════════════════════
# API ROUTES: Notification Creation (for internal use)
# ═══════════════════════════════════════════════════════════════════════════

@notifications_bp.route('/api/notifications/create', methods=['POST'])
def api_create_notification():
    """
    Internal endpoint to create notifications.
    Should be called from other route handlers or services.
    """
    # This endpoint can be restricted to internal use only
    data = request.get_json()

    required_fields = ['recipient_id', 'recipient_type', 'title', 'message', 'notification_type']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400

    notification = NotificationService.create_notification(
        recipient_id=data['recipient_id'],
        recipient_type=data['recipient_type'],
        title=data['title'],
        message=data['message'],
        notification_type=data['notification_type'],
        related_job_id=data.get('related_job_id'),
        related_seeker_id=data.get('related_seeker_id'),
        related_company_id=data.get('related_company_id'),
        related_application_id=data.get('related_application_id'),
        action_url=data.get('action_url'),
    )

    if notification:
        return jsonify({
            'success': True,
            'notification': notification.to_dict(),
        }), 201
    else:
        return jsonify({'error': 'Failed to create notification'}), 500


