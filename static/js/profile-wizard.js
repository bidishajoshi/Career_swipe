/**
 * CareerSwipe Profile Wizard – shared utilities
 * Validation, autosave, drag-drop uploads, toasts, completion meter
 */
(function (global) {
  'use strict';

  function showToast(message, type) {
    type = type || 'info';
    var container = document.getElementById('wizard-toast-container');
    if (!container) {
      container = document.createElement('div');
      container.id = 'wizard-toast-container';
      container.className = 'notif-toasts';
      document.body.appendChild(container);
    }
    var icons = { success: '✅', error: '❌', warning: '⚠️', info: 'ℹ️' };
    var item = document.createElement('div');
    item.className = 'toast-item toast-' + type;
    item.innerHTML =
      '<span class="toast-icon">' + (icons[type] || icons.info) + '</span>' +
      '<div class="toast-content"><p>' + message + '</p></div>';
    container.appendChild(item);
    setTimeout(function () {
      item.classList.add('hide');
      setTimeout(function () { item.remove(); }, 400);
    }, 3500);
  }

  function createErrorElement(message) {
    var error = document.createElement('div');
    error.className = 'field-error';
    error.textContent = message;
    return error;
  }

  function clearFieldError(field) {
    var parent = field.closest('.field') || field.parentElement;
    var existing = parent.querySelector('.field-error');
    if (existing) existing.remove();
    if (field.type !== 'checkbox') {
      field.style.borderColor = '';
    } else {
      parent.style.color = '';
    }
  }

  function markFieldInvalid(field, message) {
    var parent = field.closest('.field') || field.parentElement;
    var error = parent.querySelector('.field-error');
    if (!error) {
      error = createErrorElement(message);
      parent.appendChild(error);
    } else {
      error.textContent = message;
    }
    if (field.type === 'checkbox') {
      parent.style.color = '#ef4444';
    } else {
      field.style.borderColor = '#ef4444';
    }
  }

  function validateStep(stepEl) {
    if (!stepEl) return true;
    var requiredFields = stepEl.querySelectorAll('[required]');
    var valid = true;
    requiredFields.forEach(function (field) {
      clearFieldError(field);
      if (field.type === 'checkbox') {
        if (!field.checked) {
          markFieldInvalid(field, 'This field is required.');
          valid = false;
        }
      } else if (field.type === 'file') {
        if (!field.files.length && !field.dataset.hasExisting) {
          markFieldInvalid(field, 'Please upload a file.');
          valid = false;
        }
      } else if (!field.value || !field.checkValidity()) {
        var label = field.closest('.field');
        label = label ? label.querySelector('label') : null;
        var cleanLabel = label ? label.innerText.replace('*', '').trim() : 'This field';
        markFieldInvalid(field, cleanLabel + ' is required.');
        valid = false;
      }
    });
    if (!valid) {
      var firstError = stepEl.querySelector('.field-error');
      if (firstError) firstError.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }
    return valid;
  }

  function updateProgressBar(step, totalSteps, prefix) {
    prefix = prefix || 'prog-step-';
    document.querySelectorAll('.step-item').forEach(function (item, index) {
      var stepNum = index + 1;
      item.classList.remove('active', 'completed');
      if (stepNum < step) item.classList.add('completed');
      else if (stepNum === step) item.classList.add('active');
    });
  }

  function updateCompletionMeter(form, fieldSelectors) {
    var meter = document.getElementById('wizard-completion-fill');
    var pctEl = document.getElementById('wizard-completion-pct');
    if (!meter || !form) return;
    var total = fieldSelectors.length;
    var filled = 0;
    fieldSelectors.forEach(function (sel) {
      var el = form.querySelector(sel);
      if (!el) return;
      if (el.type === 'checkbox') {
        if (el.checked) filled++;
      } else if (el.type === 'file') {
        if (el.files.length || el.dataset.hasExisting) filled++;
      } else if (el.value && el.value.trim()) {
        filled++;
      }
    });
    var pct = total ? Math.round((filled / total) * 100) : 0;
    meter.style.width = pct + '%';
    if (pctEl) pctEl.textContent = pct + '%';
    return pct;
  }

  function setupAutosave(form, url, role, intervalMs) {
    if (!form || !url) return;
    intervalMs = intervalMs || 15000;
    var indicator = document.getElementById('autosave-indicator');
    var timer = null;

    function collectData() {
      var data = new FormData(form);
      data.set('role', role);
      return data;
    }

    function saveDraft() {
      if (indicator) {
        indicator.textContent = 'Saving…';
        indicator.classList.add('saving');
      }
      fetch(url, { method: 'POST', body: collectData(), credentials: 'same-origin' })
        .then(function (r) { return r.json(); })
        .then(function (res) {
          if (indicator) {
            indicator.textContent = res.saved_at ? 'Saved ' + res.saved_at : 'Draft saved';
            indicator.classList.remove('saving');
          }
        })
        .catch(function () {
          if (indicator) indicator.textContent = 'Autosave unavailable';
        });
    }

    form.addEventListener('input', function () {
      clearTimeout(timer);
      timer = setTimeout(saveDraft, intervalMs);
      if (indicator) indicator.textContent = 'Unsaved changes';
    });
  }

  function setupDragDrop(dropZone, fileInput, onFile) {
    if (!dropZone || !fileInput) return;
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(function (ev) {
      dropZone.addEventListener(ev, function (e) {
        e.preventDefault();
        e.stopPropagation();
      });
    });
    dropZone.addEventListener('dragover', function () {
      dropZone.classList.add('drag-over');
    });
    ['dragleave', 'drop'].forEach(function (ev) {
      dropZone.addEventListener(ev, function () {
        dropZone.classList.remove('drag-over');
      });
    });
    dropZone.addEventListener('drop', function (e) {
      var file = e.dataTransfer.files[0];
      if (!file) return;
      var dt = new DataTransfer();
      dt.items.add(file);
      fileInput.files = dt.files;
      if (onFile) onFile(file);
    });
    fileInput.addEventListener('change', function () {
      if (fileInput.files[0] && onFile) onFile(fileInput.files[0]);
    });
  }

  function setupFileDisplay(inputId, displayId, cardId) {
    var input = document.getElementById(inputId);
    var display = document.getElementById(displayId);
    var card = cardId ? document.getElementById(cardId) : null;
    if (!input) return;
    input.addEventListener('change', function () {
      var file = input.files[0];
      if (display) display.textContent = file ? file.name : 'No file chosen';
      if (card && file) card.style.display = 'flex';
    });
  }

  global.ProfileWizard = {
    showToast: showToast,
    validateStep: validateStep,
    updateProgressBar: updateProgressBar,
    updateCompletionMeter: updateCompletionMeter,
    setupAutosave: setupAutosave,
    setupDragDrop: setupDragDrop,
    setupFileDisplay: setupFileDisplay,
    markFieldInvalid: markFieldInvalid,
    clearFieldError: clearFieldError,
  };
})(window);
