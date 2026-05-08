/* ══════════════════════════════════════════════════════════════════════════
   CareerSwipe · swipe.js  — Touch + Mouse + Keyboard swipe logic
   ══════════════════════════════════════════════════════════════════════════ */
(function () {
  'use strict';

  const stack      = document.getElementById('swipeStack');
  const btnSkip    = document.getElementById('btnSkip');
  const btnApply   = document.getElementById('btnApply');
  const overlaySkip  = document.getElementById('overlaySkip');
  const overlayApply = document.getElementById('overlayApply');

  if (!stack) return;

  /* ── State ────────────────────────────────────────────────────────────── */
  let isDragging  = false;
  let startX      = 0;
  let startY      = 0;
  let currentX    = 0;
  let lastX       = 0;
  let velocity    = 0;
  let lastTime    = 0;
  let activeCard  = null;
  let isBusy      = false;   // debounce rapid swipes

  const SWIPE_THRESHOLD  = 80;   // px before triggering swipe
  const VELOCITY_THRESHOLD = 0.4; // px/ms – fast flick triggers swipe

  /* ── Helpers ──────────────────────────────────────────────────────────── */
  function getTopCard() {
    const cards = stack.querySelectorAll('.job-card:not(.fly-right):not(.fly-left)');
    return cards[cards.length - 1] || null;
  }

  function resetCard(card) {
    card.style.transform  = '';
    card.style.transition = '';
    card.classList.remove('swiping-right', 'swiping-left');
  }

  function setDragState(card, deltaX) {
    const rotate = deltaX * 0.07;
    card.style.transform = `translateX(${deltaX}px) rotate(${rotate}deg)`;

    if (deltaX > 50) {
      card.classList.add('swiping-right');
      card.classList.remove('swiping-left');
    } else if (deltaX < -50) {
      card.classList.add('swiping-left');
      card.classList.remove('swiping-right');
    } else {
      card.classList.remove('swiping-right', 'swiping-left');
    }
  }

  /* ── Mouse drag ───────────────────────────────────────────────────────── */
  stack.addEventListener('mousedown', e => {
    const card = e.target.closest('.job-card');
    if (!card || card !== getTopCard() || isBusy) return;

    isDragging = true;
    activeCard = card;
    startX     = e.clientX;
    startY     = e.clientY;
    lastX      = e.clientX;
    lastTime   = Date.now();
    velocity   = 0;
    card.style.transition = 'none';
    e.preventDefault();
  });

  document.addEventListener('mousemove', e => {
    if (!isDragging || !activeCard) return;
    const now   = Date.now();
    const dt    = now - lastTime;
    if (dt > 0) velocity = (e.clientX - lastX) / dt;
    lastX    = e.clientX;
    lastTime = now;

    currentX = e.clientX - startX;
    setDragState(activeCard, currentX);
  });

  document.addEventListener('mouseup', () => {
    if (!isDragging || !activeCard) return;
    isDragging = false;

    const absV = Math.abs(velocity);
    if (currentX > SWIPE_THRESHOLD || (absV > VELOCITY_THRESHOLD && currentX > 20)) {
      doSwipe(activeCard, 'right');
    } else if (currentX < -SWIPE_THRESHOLD || (absV > VELOCITY_THRESHOLD && currentX < -20)) {
      doSwipe(activeCard, 'left');
    } else {
      activeCard.style.transition = 'transform 0.4s cubic-bezier(0.23, 1, 0.32, 1)';
      resetCard(activeCard);
    }
    activeCard = null;
    currentX   = 0;
    velocity   = 0;
  });

  /* ── Touch events ─────────────────────────────────────────────────────── */
  let touchStartX = 0;
  let touchStartY = 0;
  let touchLocked = false;  // prevent vertical scroll interference

  stack.addEventListener('touchstart', e => {
    const card = e.target.closest('.job-card');
    if (!card || card !== getTopCard() || isBusy) return;

    isDragging  = true;
    activeCard  = card;
    touchLocked = false;
    startX      = e.touches[0].clientX;
    startY      = e.touches[0].clientY;
    touchStartX = e.touches[0].clientX;
    touchStartY = e.touches[0].clientY;
    lastX       = e.touches[0].clientX;
    lastTime    = Date.now();
    velocity    = 0;
    card.style.transition = 'none';
  }, { passive: true });

  stack.addEventListener('touchmove', e => {
    if (!isDragging || !activeCard) return;

    const tx = e.touches[0].clientX;
    const ty = e.touches[0].clientY;

    // Determine if horizontal vs vertical intent
    if (!touchLocked) {
      const dX = Math.abs(tx - touchStartX);
      const dY = Math.abs(ty - touchStartY);
      if (dX > 5 || dY > 5) {
        touchLocked = true;
        if (dY > dX) {
          // Vertical scroll intent – abort drag
          isDragging = false;
          resetCard(activeCard);
          activeCard = null;
          return;
        }
      }
    }

    const now = Date.now();
    const dt  = now - lastTime;
    if (dt > 0) velocity = (tx - lastX) / dt;
    lastX    = tx;
    lastTime = now;

    currentX = tx - startX;
    setDragState(activeCard, currentX);

    // Prevent page scroll when swiping horizontally
    if (Math.abs(currentX) > 10) {
      e.preventDefault();
    }
  }, { passive: false });

  stack.addEventListener('touchend', () => {
    if (!isDragging || !activeCard) return;
    isDragging = false;

    const absV = Math.abs(velocity);
    if (currentX > SWIPE_THRESHOLD || (absV > VELOCITY_THRESHOLD && currentX > 20)) {
      doSwipe(activeCard, 'right');
    } else if (currentX < -SWIPE_THRESHOLD || (absV > VELOCITY_THRESHOLD && currentX < -20)) {
      doSwipe(activeCard, 'left');
    } else {
      activeCard.style.transition = 'transform 0.4s cubic-bezier(0.23, 1, 0.32, 1)';
      resetCard(activeCard);
    }
    activeCard = null;
    currentX   = 0;
    velocity   = 0;
  });

  /* ── Keyboard ─────────────────────────────────────────────────────────── */
  document.addEventListener('keydown', e => {
    if (isBusy) return;
    const card = getTopCard();
    if (!card) return;
    if (e.key === 'ArrowRight') doSwipe(card, 'right');
    if (e.key === 'ArrowLeft')  doSwipe(card, 'left');
  });

  /* ── Buttons ──────────────────────────────────────────────────────────── */
  btnSkip?.addEventListener('click', () => {
    if (isBusy) return;
    const card = getTopCard();
    if (card) doSwipe(card, 'left');
  });

  btnApply?.addEventListener('click', () => {
    if (isBusy) return;
    const card = getTopCard();
    if (card) doSwipe(card, 'right');
  });

  /* ── Core swipe ───────────────────────────────────────────────────────── */
  function doSwipe(card, direction) {
    if (isBusy) return;
    isBusy = true;

    const jobId = card.dataset.jobId;

    // Fly-away
    card.style.transition = '';
    card.classList.remove('swiping-right', 'swiping-left');
    card.classList.add(direction === 'right' ? 'fly-right' : 'fly-left');
    card.style.pointerEvents = 'none';

    // Feedback overlay
    const overlay = direction === 'right' ? overlayApply : overlaySkip;
    if (overlay) {
      overlay.classList.add('show');
      setTimeout(() => overlay.classList.remove('show'), 800);
    }

    // Disable cards below to prevent accidental interaction
    const nextCard = getNextCard(card);

    // POST to server (non-blocking)
    fetchSwipe(jobId, direction).then(data => {
      if (data?.direction === 'right') {
        showToast('✅ Application sent!', 'success');
      }
    }).catch(() => {
      showToast('⚠️ Connection issue. Swipe saved locally.', 'warning');
    });

    // Remove card after animation
    setTimeout(() => {
      card.remove();
      isBusy = false;

      // Make next card interactive
      const top = getTopCard();
      if (!top) {
        showAllDoneMessage();
      }
    }, 440);
  }

  function getNextCard(currentCard) {
    const cards = stack.querySelectorAll('.job-card:not(.fly-right):not(.fly-left)');
    for (let i = cards.length - 1; i >= 0; i--) {
      if (cards[i] !== currentCard) return cards[i];
    }
    return null;
  }

  async function fetchSwipe(jobId, direction) {
    const resp = await fetch('/swipe', {
      method:  'POST',
      headers: { 'Content-Type': 'application/json' },
      body:    JSON.stringify({ job_id: jobId, direction }),
    });
    if (!resp.ok) throw new Error('Network response was not ok');
    return resp.json();
  }

  /* ── All done ─────────────────────────────────────────────────────────── */
  function showAllDoneMessage() {
    stack.innerHTML = `
      <div class="all-done" style="
        display:flex; flex-direction:column; align-items:center; justify-content:center;
        height:100%; text-align:center; padding:3rem 1.5rem; gap:1rem;
        background: rgba(10,22,40,0.6); backdrop-filter:blur(16px);
        border-radius:28px; border:1px solid rgba(59,130,246,0.15);
      ">
        <div style="font-size:3.5rem; animation: floatBounce 2s ease-in-out infinite;">🎉</div>
        <h3 style="font-family:'Syne',sans-serif;font-size:1.4rem;font-weight:800;color:#f0f6ff;margin:0">
          You've seen all jobs!
        </h3>
        <p style="font-size:14px;color:#6b87a8;max-width:260px;line-height:1.6">
          Check back later for new listings or update your filters.
        </p>
        <a href="window.location.reload()" onclick="window.location.reload();return false;"
           style="margin-top:0.5rem;background:linear-gradient(135deg,#3b82f6,#2563eb);
           color:#fff;padding:10px 24px;border-radius:12px;text-decoration:none;
           font-weight:600;font-size:14px;border:none;cursor:pointer;
           box-shadow:0 4px 20px rgba(59,130,246,0.35);">
          🔄 Refresh Jobs
        </a>
      </div>`;

    // Inject required keyframe if not present
    if (!document.getElementById('floatBounce')) {
      const style = document.createElement('style');
      style.id = 'floatBounce';
      style.textContent = '@keyframes floatBounce{0%,100%{transform:translateY(0)}50%{transform:translateY(-12px)}}';
      document.head.appendChild(style);
    }
  }

  /* ── Toast ────────────────────────────────────────────────────────────── */
  function showToast(msg, type = 'success') {
    // Remove any existing toasts
    document.querySelectorAll('.cs-toast').forEach(t => t.remove());

    const colors = {
      success: { bg: 'rgba(16,185,129,0.15)', border: 'rgba(16,185,129,0.4)', text: '#34d399' },
      warning: { bg: 'rgba(245,158,11,0.15)',  border: 'rgba(245,158,11,0.4)',  text: '#fbbf24' },
      error:   { bg: 'rgba(239,68,68,0.15)',   border: 'rgba(239,68,68,0.4)',   text: '#f87171' },
    };
    const c = colors[type] || colors.success;

    const t = document.createElement('div');
    t.className = 'cs-toast';
    t.textContent = msg;
    t.style.cssText = `
      position:fixed; bottom:2rem; left:50%; transform:translateX(-50%) translateY(20px);
      background:${c.bg}; color:${c.text}; border:1px solid ${c.border};
      padding:11px 22px; border-radius:100px; font-size:14px; font-weight:600;
      z-index:99999; backdrop-filter:blur(12px);
      opacity:0; transition:opacity 0.3s, transform 0.3s;
      white-space:nowrap; max-width:90vw;
    `;
    document.body.appendChild(t);
    requestAnimationFrame(() => {
      t.style.opacity   = '1';
      t.style.transform = 'translateX(-50%) translateY(0)';
    });
    setTimeout(() => {
      t.style.opacity   = '0';
      t.style.transform = 'translateX(-50%) translateY(10px)';
      setTimeout(() => t.remove(), 320);
    }, 2800);
  }
})();
