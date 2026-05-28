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
