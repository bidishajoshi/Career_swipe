/* ══════════════════════════════════════════════════════════════════════════
   CareerSwipe · main.js
   ══════════════════════════════════════════════════════════════════════════ */
document.addEventListener('DOMContentLoaded', () => {

  /* ── Theme Toggle ─────────────────────────────────────────────────────── */
  const themeToggle = document.getElementById('themeToggle');
  const body        = document.body;

  if (themeToggle) {
    themeToggle.addEventListener('click', () => {
      const isLight = body.classList.toggle('light-mode');
      localStorage.setItem('theme', isLight ? 'light' : 'dark');
      document.cookie = `theme=${isLight ? 'light' : 'dark'}; path=/; max-age=31536000`;
    });
  }

  /* ── Mobile Menu Toggle ───────────────────────────────────────────────── */
  const menuToggle = document.getElementById('menuToggle');
  const navLinks   = document.getElementById('navLinks');

  if (menuToggle && navLinks) {
    menuToggle.addEventListener('click', e => {
      e.stopPropagation();
      const isOpen = navLinks.classList.toggle('active');
      menuToggle.classList.toggle('is-active', isOpen);
      menuToggle.setAttribute('aria-expanded', isOpen);
      // Prevent body scroll when nav is open
      body.style.overflow = isOpen ? 'hidden' : '';
    });

    // Close on outside click
    document.addEventListener('click', e => {
      if (
        navLinks.classList.contains('active') &&
        !menuToggle.contains(e.target) &&
        !navLinks.contains(e.target)
      ) {
        navLinks.classList.remove('active');
        menuToggle.classList.remove('is-active');
        body.style.overflow = '';
      }
    });

    // Close on nav link click (mobile)
    navLinks.querySelectorAll('a').forEach(link => {
      link.addEventListener('click', () => {
        navLinks.classList.remove('active');
        menuToggle.classList.remove('is-active');
        body.style.overflow = '';
      });
    });
  }

  /* ── Active Nav Link ──────────────────────────────────────────────────── */
  const currentPath = window.location.pathname;
  document.querySelectorAll('.nav-links a, .sidebar-nav a').forEach(link => {
    const href = link.getAttribute('href');
    if (href && href !== '/' && currentPath.startsWith(href)) {
      link.classList.add('active');
    }
  });

  /* ── Sticky Navbar Glass Effect on Scroll ─────────────────────────────── */
  const navbar = document.querySelector('.navbar');
  if (navbar) {
    let lastScroll = 0;
    window.addEventListener('scroll', () => {
      const scroll = window.scrollY;
      if (scroll > 10) {
        navbar.style.boxShadow = '0 4px 30px rgba(0,0,0,0.3)';
      } else {
        navbar.style.boxShadow = 'none';
      }
      lastScroll = scroll;
    }, { passive: true });
  }

  /* ── Flash Message Auto-dismiss ───────────────────────────────────────── */
  document.querySelectorAll('.flash').forEach(flash => {
    setTimeout(() => {
      flash.style.transition = 'opacity 0.5s, transform 0.5s';
      flash.style.opacity = '0';
      flash.style.transform = 'translateY(-8px)';
      setTimeout(() => flash.remove(), 500);
    }, 4500);
  });

  /* ── File Upload Label ────────────────────────────────────────────────── */
  document.querySelectorAll('input[type="file"]').forEach(input => {
    const label = input.closest('.file-upload-label') ||
                  document.querySelector(`label[for="${input.id}"]`);
    const display = label?.querySelector('.file-name-display');

    if (input && display) {
      input.addEventListener('change', () => {
        const name = input.files[0]?.name;
        display.textContent = name ? `📎 ${name}` : 'No file chosen';
      });
    }
  });

  /* ── Smooth Anchor Scrolling ──────────────────────────────────────────── */
  document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', e => {
      const target = document.querySelector(anchor.getAttribute('href'));
      if (target) {
        e.preventDefault();
        const navH = document.querySelector('.navbar')?.offsetHeight || 66;
        const sideH = window.innerWidth <= 768
          ? (document.querySelector('.sidebar')?.offsetHeight || 0)
          : 0;
        const top = target.getBoundingClientRect().top + window.scrollY - navH - sideH - 16;
        window.scrollTo({ top, behavior: 'smooth' });
      }
    });
  });

  /* ── Animate elements on scroll (Intersection Observer) ──────────────── */
  const animateEls = document.querySelectorAll(
    '.feature-card, .job-listing-card, .applicant-card, .stat-box'
  );
  if (animateEls.length && 'IntersectionObserver' in window) {
    const observer = new IntersectionObserver(entries => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.style.opacity  = '1';
          entry.target.style.transform = 'translateY(0)';
          observer.unobserve(entry.target);
        }
      });
    }, { threshold: 0.1 });

    animateEls.forEach(el => {
      el.style.opacity   = '0';
      el.style.transform = 'translateY(20px)';
      el.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
      observer.observe(el);
    });
  }

});
