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
    const mobileQuery = window.matchMedia('(max-width: 768px)');
    const applyMobileMenuFallback = () => {
      navLinks.style.position = 'fixed';
      navLinks.style.top = '66px';
      navLinks.style.right = navLinks.classList.contains('active') ? '0' : '-100%';
      navLinks.style.width = 'min(80vw, 300px)';
      navLinks.style.height = 'calc(100vh - 66px)';
      navLinks.style.flexDirection = 'column';
      navLinks.style.alignItems = 'flex-start';
    };
    const clearMobileMenuFallback = () => {
      ['position', 'top', 'right', 'width', 'height', 'flexDirection', 'alignItems'].forEach(prop => {
        navLinks.style[prop] = '';
      });
    };
    const syncMobileMenuVisibility = () => {
      if (mobileQuery.matches && !navLinks.classList.contains('active')) {
        navLinks.style.display = 'none';
      } else {
        navLinks.style.display = '';
      }
      menuToggle.style.display = mobileQuery.matches ? 'flex' : '';
      if (mobileQuery.matches) {
        applyMobileMenuFallback();
      } else {
        clearMobileMenuFallback();
      }
    };

    syncMobileMenuVisibility();
    mobileQuery.addEventListener?.('change', syncMobileMenuVisibility);

    menuToggle.addEventListener('click', e => {
      e.stopPropagation();
      navLinks.style.display = '';
      const isOpen = navLinks.classList.toggle('active');
      menuToggle.classList.toggle('is-active', isOpen);
      menuToggle.setAttribute('aria-expanded', isOpen);
      document.body.style.overflow = isOpen ? 'hidden' : '';
      if (mobileQuery.matches) applyMobileMenuFallback();
      if (!isOpen) syncMobileMenuVisibility();
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
        syncMobileMenuVisibility();
      }
    });

    navLinks.querySelectorAll('a').forEach(link => {
      link.addEventListener('click', () => {
        if (navLinks.classList.contains('active')) {
          navLinks.classList.remove('active');
          menuToggle.classList.remove('is-active');
          document.body.style.overflow = '';
          syncMobileMenuVisibility();
        }
      });
    });
  }
});
