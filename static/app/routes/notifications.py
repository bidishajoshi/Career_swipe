"""
app/routes/notifications.py – Notification routes.
Covers: notifications history page, JSON API (list, unread count, mark read).
"""

from flask import Blueprint, render_template, redirect, url_for, session, jsonify

from ..extensions import db
from ..models import Notification

notifications_bp = Blueprint('notifications', __name__)


def _current_user():
    """Return (user_id, user_type) for the logged-in user, or (None, None)."""
    if session.get('seeker_id'):
        return session['seeker_id'], 'seeker'
    if session.get('company_id'):
        return session['company_id'], 'company'
    return None, None


# ── Notifications History Page ────────────────────────────────────────────────
@notifications_bp.route('/notifications')
def notifications_history():
    user_id, user_type = _current_user()
    if not user_id:
        return redirect(url_for('auth.index'))

    notifications = (
        Notification.query
        .filter_by(user_id=user_id, user_type=user_type)
        .order_by(Notification.created_at.desc())
        .all()
    )
    return render_template('notifications.html', notifications=notifications, user_type=user_type)


# ── JSON API: List latest 10 notifications ────────────────────────────────────
@notifications_bp.route('/api/notifications')
def get_notifications():
    user_id, user_type = _current_user()
    if not user_id:
        return jsonify({'error': 'Unauthorized'}), 401

    notifs = (
        Notification.query
        .filter_by(user_id=user_id, user_type=user_type)
        .order_by(Notification.created_at.desc())
        .limit(10)
        .all()
    )
    return jsonify([n.to_dict() for n in notifs])


# ── JSON API: Unread count ────────────────────────────────────────────────────
@notifications_bp.route('/api/notifications/unread-count')
def get_unread_count():
    user_id, user_type = _current_user()
    if not user_id:
        return jsonify({'count': 0})

    count = Notification.query.filter_by(
        user_id=user_id, user_type=user_type, is_read=False
    ).count()
    return jsonify({'count': count})


# ── JSON API: Mark single notification as read ────────────────────────────────
@notifications_bp.route('/api/notifications/read/<int:notif_id>', methods=['POST'])
def mark_read(notif_id):
    user_id, user_type = _current_user()
    if not user_id:
        return jsonify({'error': 'Unauthorized'}), 401

    notif = Notification.query.get(notif_id)
    if notif and notif.user_id == user_id and notif.user_type == user_type:
        notif.is_read = True
        db.session.commit()
        return jsonify({'status': 'ok'})

    return jsonify({'error': 'Not found'}), 404


# ── JSON API: Mark all as read ────────────────────────────────────────────────
@notifications_bp.route('/api/notifications/read-all', methods=['POST'])
def mark_all_read():
    user_id, user_type = _current_user()
    if not user_id:
        return jsonify({'error': 'Unauthorized'}), 401

    Notification.query.filter_by(
        user_id=user_id, user_type=user_type, is_read=False
    ).update({'is_read': True})
    db.session.commit()
    return jsonify({'status': 'ok'})
