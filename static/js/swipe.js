/* ══════════════════════════════════════════════════════════════════════════
   CareerSwipe · swipe.js
   ══════════════════════════════════════════════════════════════════════════ */
(function () {
  'use strict';

  const stack       = document.getElementById('swipeStack');
  const btnSkip     = document.getElementById('btnSkip');
  const btnApply    = document.getElementById('btnApply');
  const overlaySkip = document.getElementById('overlaySkip');
  const overlayApply= document.getElementById('overlayApply');

  if (!stack) return;

  let isDragging = false;
  let startX     = 0;
  let lastX      = 0;
  let currentX   = 0;
  let velocity   = 0;
  let lastTime   = 0;
  let activeCard = null;
  let isBusy     = false;
  let rafId      = 0;

  const SWIPE_THRESHOLD   = 80;
  const VELOCITY_THRESHOLD= 0.4;

  function getTopCard() {
    const cards = stack.querySelectorAll('.job-card:not(.fly-right):not(.fly-left)');
    return cards[cards.length - 1] || null;
  }

  function resetCard(card) {
    if (rafId) {
      cancelAnimationFrame(rafId);
      rafId = 0;
    }
    card.style.transform  = '';
    card.style.transition = '';
    card.classList.remove('swiping-right', 'swiping-left');
  }

  function setDragState(card, deltaX) {
    const rotate = deltaX * 0.07;
    if (rafId) cancelAnimationFrame(rafId);
    rafId = requestAnimationFrame(() => {
      card.style.transform = `translate3d(${deltaX}px, 0, 0) rotate(${rotate}deg)`;
      rafId = 0;
    });

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

  function startDrag(card, clientX, clientY, pointerId) {
    if (!card || card !== getTopCard() || isBusy) return false;

    isDragging = true;
    activeCard = card;
    startX     = clientX;
    lastX      = clientX;
    lastTime   = Date.now();
    currentX   = 0;
    velocity   = 0;
    card.style.transition = 'none';

    if (pointerId !== undefined && card.setPointerCapture) {
      try { card.setPointerCapture(pointerId); } catch (err) {}
    }
    return true;
  }

  function moveDrag(clientX) {
    if (!isDragging || !activeCard) return;
    const now = Date.now();
    const dt  = now - lastTime;
    if (dt > 0) velocity = (clientX - lastX) / dt;
    lastX    = clientX;
    lastTime = now;
    currentX = clientX - startX;
    setDragState(activeCard, currentX);
  }

  function finishDrag() {
    if (!isDragging || !activeCard) return;
    isDragging = false;

    const card = activeCard;
    const absV = Math.abs(velocity);
    if (currentX > SWIPE_THRESHOLD || (absV > VELOCITY_THRESHOLD && currentX > 20)) {
      doSwipe(card, 'right');
    } else if (currentX < -SWIPE_THRESHOLD || (absV > VELOCITY_THRESHOLD && currentX < -20)) {
      doSwipe(card, 'left');
    } else {
      card.style.transition = 'transform 0.4s cubic-bezier(0.23, 1, 0.32, 1)';
      resetCard(card);
    }
    activeCard = null;
    currentX   = 0;
    velocity   = 0;
  }

  function doSwipe(card, direction) {
    if (isBusy) return;
    isBusy = true;
    if (rafId) {
      cancelAnimationFrame(rafId);
      rafId = 0;
    }

    const jobId = card.dataset.jobId;
    let shouldRemoveCard = true;
    card.style.transition = '';
    card.classList.remove('swiping-right', 'swiping-left');
    card.classList.add(direction === 'right' ? 'fly-right' : 'fly-left');
    card.style.pointerEvents = 'none';

    const overlay = direction === 'right' ? overlayApply : overlaySkip;
    if (overlay) {
      overlay.classList.add('show');
      setTimeout(() => overlay.classList.remove('show'), 800);
    }

    fetchSwipe(jobId, direction).then(data => {
      if (data?.direction === 'right') {
        showToast('✅ Application sent!', 'success');
      }
    }).catch(error => {
      shouldRemoveCard = false;
      card.classList.remove('fly-right', 'fly-left');
      card.style.pointerEvents = '';
      resetCard(card);
      showToast(error.message || 'Unable to submit. Please try again.', 'warning');
    });

    setTimeout(() => {
      if (!shouldRemoveCard) {
        isBusy = false;
        return;
      }
      card.remove();
      isBusy = false;
      const top = getTopCard();
      if (!top) {
        showToast('All done! No more jobs available.', 'info');
      }
    }, 440);
  }

  function fetchSwipe(jobId, direction) {
    const csrfToken = document.querySelector('meta[name="csrf-token"]')?.getAttribute('content');
    return fetch('/swipe', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...(csrfToken ? { 'X-CSRFToken': csrfToken } : {}),
      },
      body: JSON.stringify({ job_id: jobId, direction: direction }),
    }).then(async response => {
      const data = await response.json().catch(() => ({}));
      if (!response.ok) {
        throw new Error(data.error || 'Unable to submit. Please try again.');
      }
      return data;
    });
  }

  function addButtonListeners() {
    if (btnSkip) {
      btnSkip.addEventListener('click', () => {
        const top = getTopCard();
        if (top) doSwipe(top, 'left');
      });
    }
    if (btnApply) {
      btnApply.addEventListener('click', () => {
        const top = getTopCard();
        if (top) doSwipe(top, 'right');
      });
    }
  }

  if (window.PointerEvent) {
    stack.addEventListener('pointerdown', e => {
      if (e.pointerType === 'mouse' && e.button !== 0) return;
      const card = e.target.closest('.job-card');
      if (startDrag(card, e.clientX, e.clientY, e.pointerId)) {
        e.preventDefault();
      }
    });

    stack.addEventListener('pointermove', e => {
      if (!isDragging || !activeCard) return;
      moveDrag(e.clientX);
      if (Math.abs(currentX) > 8) e.preventDefault();
    });

    stack.addEventListener('pointerup', finishDrag);
    stack.addEventListener('pointercancel', () => {
      if (activeCard) resetCard(activeCard);
      isDragging = false;
      activeCard = null;
      currentX = 0;
      velocity = 0;
    });
  } else {
    stack.addEventListener('mousedown', e => {
      const card = e.target.closest('.job-card');
      if (!card || card !== getTopCard() || isBusy) return;
      isDragging = true;
      activeCard = card;
      startX     = e.clientX;
      lastX      = e.clientX;
      lastTime   = Date.now();
      velocity   = 0;
      card.style.transition = 'none';
      e.preventDefault();
    });

    document.addEventListener('mousemove', e => {
      if (!isDragging || !activeCard) return;
      const now = Date.now();
      const dt  = now - lastTime;
      if (dt > 0) velocity = (e.clientX - lastX) / dt;
      lastX    = e.clientX;
      lastTime = now;
      currentX = e.clientX - startX;
      setDragState(activeCard, currentX);
    });

    document.addEventListener('mouseup', () => {
      if (!isDragging || !activeCard) return;
      finishDrag();
    });
  }

  addButtonListeners();
})();
