/**
 * Flatpickr Segmented AM / PM Toggle
 * Replaces the single "lightswitch" AM/PM button with a modern tab-style segmented control [ AM | PM ]
 * where both options are visible side-by-side and the active selection is clearly highlighted.
 */
(function () {
  'use strict';

  function setupSegmentedAmPm(timeContainer) {
    if (!timeContainer || timeContainer.querySelector('.flatpickr-am-pm-segmented')) return;
    const originalAmPm = timeContainer.querySelector('.flatpickr-am-pm');
    if (!originalAmPm) return;

    // Hide original lightswitch span safely
    originalAmPm.style.setProperty('display', 'none', 'important');

    // Create Segmented Toggle Container
    const segmented = document.createElement('div');
    segmented.className = 'flatpickr-am-pm-segmented';
    segmented.setAttribute('role', 'tablist');
    segmented.setAttribute('aria-label', 'AM or PM');

    const btnAm = document.createElement('button');
    btnAm.type = 'button';
    btnAm.className = 'am-pm-tab';
    btnAm.dataset.period = 'AM';
    btnAm.setAttribute('role', 'tab');
    btnAm.setAttribute('aria-selected', 'false');
    btnAm.textContent = 'AM';

    const btnPm = document.createElement('button');
    btnPm.type = 'button';
    btnPm.className = 'am-pm-tab';
    btnPm.dataset.period = 'PM';
    btnPm.setAttribute('role', 'tab');
    btnPm.setAttribute('aria-selected', 'false');
    btnPm.textContent = 'PM';

    segmented.appendChild(btnAm);
    segmented.appendChild(btnPm);
    timeContainer.appendChild(segmented);

    function syncState() {
      const current = (originalAmPm.textContent || '').trim().toUpperCase();
      if (current === 'PM') {
        btnPm.classList.add('is-active');
        btnPm.setAttribute('aria-selected', 'true');
        btnAm.classList.remove('is-active');
        btnAm.setAttribute('aria-selected', 'false');
      } else {
        btnAm.classList.add('is-active');
        btnAm.setAttribute('aria-selected', 'true');
        btnPm.classList.remove('is-active');
        btnPm.setAttribute('aria-selected', 'false');
      }
    }

    btnAm.addEventListener('click', function (e) {
      e.preventDefault();
      e.stopPropagation();
      const current = (originalAmPm.textContent || '').trim().toUpperCase();
      if (current !== 'AM') {
        originalAmPm.click();
      }
      syncState();
    });

    btnPm.addEventListener('click', function (e) {
      e.preventDefault();
      e.stopPropagation();
      const current = (originalAmPm.textContent || '').trim().toUpperCase();
      if (current !== 'PM') {
        originalAmPm.click();
      }
      syncState();
    });

    // Observe textContent changes (e.g. When hour rolls over 12 through typing or spinner)
    const observer = new MutationObserver(syncState);
    observer.observe(originalAmPm, { characterData: true, childList: true, subtree: true });

    // Initial state sync
    syncState();
  }

  // Expose globally for manual calls if needed
  window.enhanceFlatpickrAmPm = setupSegmentedAmPm;

  // Automatically observe all flatpickr-time containers inserted into the DOM
  function scanAndEnhance() {
    document.querySelectorAll('.flatpickr-time').forEach(setupSegmentedAmPm);
  }

  if (typeof MutationObserver !== 'undefined') {
    const bodyObserver = new MutationObserver(function () {
      scanAndEnhance();
    });
    if (document.body) {
      bodyObserver.observe(document.body, { childList: true, subtree: true });
    } else {
      document.addEventListener('DOMContentLoaded', function () {
        bodyObserver.observe(document.body, { childList: true, subtree: true });
        scanAndEnhance();
      });
    }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', scanAndEnhance);
  } else {
    scanAndEnhance();
  }
})();

