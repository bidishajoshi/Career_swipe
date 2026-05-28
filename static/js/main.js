/* ══════════════════════════════════════════════════════════════════════════
   CareerSwipe · main.js
   ══════════════════════════════════════════════════════════════════════════ */

document.addEventListener('DOMContentLoaded', () => {
  const themeToggle = document.getElementById('themeToggle');
  const body        = document.body;

  if (localStorage.getItem('theme') === 'light' || document.cookie.includes('theme=light')) {
    body.classList.add('light-mode');
  }

  if (themeToggle) {
    themeToggle.addEventListener('click', () => {
      const isLight = body.classList.toggle('light-mode');
      localStorage.setItem('theme', isLight ? 'light' : 'dark');
      document.cookie = `theme=${isLight ? 'light' : 'dark'}; path=/; max-age=31536000`;
    });
  }

  const menuToggle = document.getElementById('menuToggle');
  const navLinks   = document.getElementById('navLinks');

  if (menuToggle && navLinks) {
    menuToggle.addEventListener('click', e => {
      e.stopPropagation();
      const isOpen = navLinks.classList.toggle('active');
      menuToggle.classList.toggle('is-active', isOpen);
      menuToggle.setAttribute('aria-expanded', isOpen);
      document.body.style.overflow = isOpen ? 'hidden' : '';
    });

    document.addEventListener('click', e => {
      if (
        navLinks.classList.contains('active') &&
        !menuToggle.contains(e.target) &&
        !navLinks.contains(e.target)
      ) {
        navLinks.classList.remove('active');
        menuToggle.classList.remove('is-active');
        document.body.style.overflow = '';
      }
    });

    navLinks.querySelectorAll('a').forEach(link => {
      link.addEventListener('click', () => {
        if (navLinks.classList.contains('active')) {
          navLinks.classList.remove('active');
          menuToggle.classList.remove('is-active');
          document.body.style.overflow = '';
        }
      });
    });
  }
});
