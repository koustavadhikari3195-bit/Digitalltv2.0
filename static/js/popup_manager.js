/**
 * DIGITALLY — Gatekeeper Popup Manager
 * Shows once per user. Skippable. Memorable.
 */
(function () {
  'use strict';

  const STORAGE_KEY = 'digitally_gate_v1';
  const DELAY_MS = 4000;
  const modal = document.getElementById('gatekeeper-modal');
  const skipBtn = document.getElementById('gatekeeper-skip');

  if (!modal) return;

  function openModal() {
    modal.classList.remove('hidden');
    modal.style.animation = 'fadeInScale 0.3s ease-out forwards';
    localStorage.setItem(STORAGE_KEY, 'shown');
  }

  function closeModal() {
    modal.style.animation = 'fadeOutScale 0.2s ease-in forwards';
    setTimeout(() => modal.classList.add('hidden'), 200);
  }

  // Close on backdrop click
  modal.addEventListener('click', (e) => { if (e.target === modal) closeModal(); });

  // Skip button
  skipBtn?.addEventListener('click', closeModal);

  // Close after successful HTMX form submission
  document.body.addEventListener('htmx:afterRequest', (e) => {
    if (e.detail.elt.closest('form') && e.detail.xhr.status === 200) {
      setTimeout(closeModal, 1500);
    }
  });

  // Fire once
  if (!localStorage.getItem(STORAGE_KEY)) {
    setTimeout(openModal, DELAY_MS);
  }
})();
