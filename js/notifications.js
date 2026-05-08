/**
 * CareerSwipe - Notification System Logic
 * Handles real-time polling, toasts, and dropdown UI.
 */

document.addEventListener('DOMContentLoaded', () => {
    const notifBell = document.getElementById('notifBell');
    const notifBadge = document.getElementById('notifBadge');
    const notifDropdown = document.getElementById('notifDropdown');
    const notifList = document.getElementById('notifList');
    const markAllReadBtn = document.getElementById('markAllRead');
    const toastContainer = document.getElementById('notif-toasts');

    let lastCount = 0;
    let isPolling = true;

    // ── Polling Logic ───────────────────────────────────────────────────────
    async function checkNotifications() {
        if (!isPolling) return;

        try {
            const res = await fetch('/api/notifications/unread-count');
            const data = await res.json();
            const count = data.count || 0;

            if (count > lastCount) {
                // New notification arrived!
                updateBadge(count);
                fetchLatestAndToast();
            } else if (count !== lastCount) {
                updateBadge(count);
            }
            lastCount = count;
        } catch (err) {
            console.error('Polling error:', err);
        }
    }

    function updateBadge(count) {
        if (count > 0) {
            notifBadge.textContent = count > 99 ? '99+' : count;
            notifBadge.style.display = 'flex';
        } else {
            notifBadge.style.display = 'none';
        }
    }

    async function fetchLatestAndToast() {
        try {
            const res = await fetch('/api/notifications');
            const notifications = await res.json();
            if (notifications.length > 0) {
                const latest = notifications[0];
                // Only toast if it's unread and very recent (optional check)
                if (!latest.is_read) {
                    showToast(latest);
                }
            }
        } catch (err) {
            console.error('Fetch error:', err);
        }
    }

    // ── Toast Logic ──────────────────────────────────────────────────────────
    function showToast(notif) {
        const toast = document.createElement('div');
        toast.className = 'toast-item';
        
        let icon = '🔔';
        if (notif.type === 'application') icon = '💼';
        if (notif.type === 'accepted') icon = '🎉';
        if (notif.type === 'rejected') icon = '❌';
        if (notif.type === 'interview') icon = '📅';

        toast.innerHTML = `
            <div class="toast-icon">${icon}</div>
            <div class="toast-content">
                <p>${notif.message}</p>
            </div>
        `;

        toastContainer.appendChild(toast);

        // Play subtle sound (optional)
        // const audio = new Audio('/static/sounds/notif.mp3');
        // audio.play();

        setTimeout(() => {
            toast.classList.add('hide');
            setTimeout(() => toast.remove(), 400);
        }, 5000);
    }

    // ── Dropdown Logic ───────────────────────────────────────────────────────
    if (notifBell) {
        notifBell.addEventListener('click', (e) => {
            e.stopPropagation();
            notifDropdown.classList.toggle('show');
            if (notifDropdown.classList.contains('show')) {
                loadDropdownList();
            }
        });
    }

    async function loadDropdownList() {
        notifList.innerHTML = '<div class="notif-empty">Loading...</div>';
        try {
            const res = await fetch('/api/notifications');
            const notifications = await res.json();
            
            if (notifications.length === 0) {
                notifList.innerHTML = '<div class="notif-empty">No notifications yet</div>';
                return;
            }

            notifList.innerHTML = '';
            notifications.forEach(n => {
                const item = document.createElement('div');
                item.className = `notif-item ${n.is_read ? '' : 'unread'}`;
                item.innerHTML = `
                    <div class="notif-item-body">
                        <p class="item-notif-msg">${n.message}</p>
                        <span class="item-notif-time">${n.created_at}</span>
                    </div>
                `;
                item.addEventListener('click', async () => {
                    if (!n.is_read) {
                        await markAsRead(n.id);
                        item.classList.remove('unread');
                    }
                    // Redirect or handle click
                });
                notifList.appendChild(item);
            });
        } catch (err) {
            notifList.innerHTML = '<div class="notif-empty">Error loading notifications</div>';
        }
    }

    async function markAsRead(id) {
        try {
            await fetch(`/api/notifications/read/${id}`, { method: 'POST' });
            checkNotifications(); // Update count
        } catch (err) { console.error(err); }
    }

    if (markAllReadBtn) {
        markAllReadBtn.addEventListener('click', async (e) => {
            e.stopPropagation();
            try {
                await fetch('/api/notifications/read-all', { method: 'POST' });
                checkNotifications();
                loadDropdownList();
            } catch (err) { console.error(err); }
        });
    }

    // Close dropdown on click outside
    document.addEventListener('click', () => {
        if (notifDropdown) notifDropdown.classList.remove('show');
    });

    // ── Initialization ──────────────────────────────────────────────────────
    checkNotifications();
    setInterval(checkNotifications, 30000); // Poll every 30s
});
