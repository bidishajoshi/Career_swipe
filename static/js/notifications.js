/* ══════════════════════════════════════════════════════════════════════════
   CareerSwipe · notifications.js
   ══════════════════════════════════════════════════════════════════════════ */

function showToast(message, type = 'info') {
  const container = document.getElementById('notif-toasts');
  if (!container) return;

  const toast = document.createElement('div');
  toast.className = `toast-item toast-${type}`;
  toast.innerHTML = `
    <div class="toast-icon">${type === 'success' ? '✅' : type === 'warning' ? '⚠️' : 'ℹ️'}</div>
    <div class="toast-content"><p>${message}</p></div>
  `;

  container.appendChild(toast);

  setTimeout(() => {
    toast.classList.add('hide');
    setTimeout(() => toast.remove(), 400);
  }, 2800);
}

function clearToasts() {
  const container = document.getElementById('notif-toasts');
  if (!container) return;
  container.innerHTML = '';
}

document.addEventListener('DOMContentLoaded', () => {
  const notifBell = document.getElementById('notifBell');
  const notifDropdown = document.getElementById('notifDropdown');
  const notifList = document.getElementById('notifList');
  const notifBadge = document.getElementById('notifBadge');
  const markAllReadButton = document.getElementById('markAllRead');

  if (!notifBell || !notifDropdown || !notifList) {
    return;
  }

  let isDropdownOpen = false;

  notifBell.addEventListener('click', async event => {
    event.stopPropagation();
    isDropdownOpen = !notifDropdown.classList.contains('show');
    notifDropdown.classList.toggle('show', isDropdownOpen);

    if (isDropdownOpen) {
      await refreshNotifications();
      document.addEventListener('click', handleOutsideClick);
    } else {
      document.removeEventListener('click', handleOutsideClick);
    }
  });

  if (markAllReadButton) {
    markAllReadButton.addEventListener('click', async event => {
      event.preventDefault();
      const success = await markAllRead();
      if (success) {
        await refreshNotifications();
      }
    });
  }

  async function handleOutsideClick(event) {
    if (!notifDropdown.contains(event.target) && event.target !== notifBell) {
      notifDropdown.classList.remove('show');
      isDropdownOpen = false;
      document.removeEventListener('click', handleOutsideClick);
    }
  }

  async function refreshNotifications() {
    await Promise.all([loadUnreadCount(), loadDropdownNotifications()]);
  }

  async function loadUnreadCount() {
    try {
      const response = await fetch('/api/notifications/unread-count');
      if (!response.ok) {
        return;
      }
      const data = await response.json();
      if (data.count > 0) {
        notifBadge.textContent = data.count;
        notifBadge.style.display = 'inline-flex';
      } else {
        notifBadge.style.display = 'none';
      }
    } catch (error) {
      console.error('Unable to fetch unread notification count:', error);
    }
  }

  async function loadDropdownNotifications() {
    try {
      notifList.innerHTML = '<div class="notif-empty">Loading notifications...</div>';
      const response = await fetch('/api/notifications?limit=50');
      if (!response.ok) {
        notifList.innerHTML = '<div class="notif-empty">Failed to load notifications.</div>';
        return;
      }

      const data = await response.json();
      const notifications = data.notifications || [];

      if (!notifications.length) {
        notifList.innerHTML = '<div class="notif-empty">No notifications yet.</div>';
        return;
      }

      notifList.innerHTML = '';
      notifications.forEach(notification => {
        const item = document.createElement('div');
        item.className = `notif-item ${notification.is_read ? '' : 'unread'}`;
        item.innerHTML = `
          <div class="notif-item-content">
            <div class="notif-item-header">
              <span class="notif-item-type">${formatNotificationType(notification.type)}</span>
              <span class="notif-item-dot ${notification.is_read ? '' : 'unread'}"></span>
            </div>
            <p class="notif-item-message">${notification.message}</p>
            <small class="notif-item-time">${formatRelativeTime(notification.created_at)}</small>
          </div>
        `;
        notifList.appendChild(item);
      });
    } catch (error) {
      console.error('Unable to load notifications:', error);
      notifList.innerHTML = '<div class="notif-empty">Unable to load notifications.</div>';
    }
  }

  function formatNotificationType(type) {
    const mapping = {
      accepted: 'Hired',
      rejected: 'Rejected',
      reject: 'Rejected',
      interview: 'Interview',
      shortlisted: 'Shortlist',
      shortlist: 'Shortlist',
      application: 'Application',
      system: 'System',
    };
    return mapping[type] || type || 'Update';
  }

  function formatRelativeTime(timestamp) {
    if (!timestamp) return '';
    const date = new Date(timestamp);
    const now = new Date();
    const diff = Math.floor((now - date) / 1000);

    if (diff < 60) return 'Just now';
    if (diff < 3600) return `${Math.floor(diff / 60)}m ago`;
    if (diff < 86400) return `${Math.floor(diff / 3600)}h ago`;
    return `${Math.floor(diff / 86400)}d ago`;
  }

  async function markAllRead() {
    try {
      const response = await fetch('/api/notifications/read-all', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      });
      if (!response.ok) {
        showToast('Unable to mark notifications read.', 'warning');
        return false;
      }
      showToast('All notifications marked as read.', 'success');
      return true;
    } catch (error) {
      console.error('Unable to mark notifications read:', error);
      showToast('Unable to mark notifications read.', 'warning');
      return false;
    }
  }

  // On page load, only fetch the unread count badge.
  // Full notification list is loaded only when the bell is clicked.
  loadUnreadCount();
});
