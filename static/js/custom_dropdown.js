/**
 * Custom Animated Dropdown for Django Admin
 * Replaces native OS system select popups with smooth up/down animated dropdowns.
 */
(function () {
  function initSelect(select) {
    if (select.dataset.customDropdownInitialized || select.multiple) return;
    select.dataset.customDropdownInitialized = 'true';

    // Hide native select from view, but keep accessible for form submission
    select.style.display = 'none';

    // Hide any duplicate sibling arrow span from Unfold
    if (select.parentElement) {
      select.parentElement.querySelectorAll(':scope > span.material-symbols-outlined').forEach(icon => {
        icon.style.display = 'none';
      });
    }

    // Container
    const container = document.createElement('div');
    container.className = 'custom-dropdown-container';

    // Trigger button
    const trigger = document.createElement('button');
    trigger.type = 'button';
    trigger.className = 'custom-dropdown-trigger';

    const labelSpan = document.createElement('span');
    labelSpan.className = 'custom-dropdown-label truncate';

    const chevron = document.createElement('span');
    chevron.className = 'material-symbols-outlined custom-dropdown-chevron text-[20px] select-none';
    chevron.textContent = 'expand_more';

    trigger.appendChild(labelSpan);
    trigger.appendChild(chevron);

    // Menu
    const menu = document.createElement('div');
    menu.className = 'custom-dropdown-menu scrollbar-default';
    menu.setAttribute('role', 'listbox');

    function updateLabel() {
      const selectedOption = select.options[select.selectedIndex];
      labelSpan.textContent = selectedOption ? selectedOption.text : 'Select value';
      // Update checkmarks in menu
      menu.querySelectorAll('.custom-dropdown-option').forEach(opt => {
        const isSel = opt.dataset.value === select.value;
        opt.classList.toggle('is-selected', isSel);
      });
    }

    function renderOptions() {
      menu.innerHTML = '';
      Array.from(select.options).forEach((opt, idx) => {
        const optionEl = document.createElement('div');
        optionEl.className = 'custom-dropdown-option';
        optionEl.dataset.value = opt.value;
        optionEl.setAttribute('role', 'option');

        const optText = document.createElement('span');
        optText.textContent = opt.text;

        const checkIcon = document.createElement('span');
        checkIcon.className = 'material-symbols-outlined custom-dropdown-check text-primary-600 dark:text-primary-400 select-none';
        checkIcon.textContent = 'check';

        optionEl.appendChild(optText);
        optionEl.appendChild(checkIcon);

        optionEl.addEventListener('click', (e) => {
          e.stopPropagation();
          select.value = opt.value;
          select.dispatchEvent(new Event('input', { bubbles: true }));
          select.dispatchEvent(new Event('change', { bubbles: true }));
          if (window.django && window.django.jQuery) {
            window.django.jQuery(select).trigger('change');
          }
          updateLabel();
          closeDropdown();
          trigger.focus();
        });

        menu.appendChild(optionEl);
      });
      updateLabel();
    }

    function openDropdown() {
      // Close other open dropdowns first
      document.querySelectorAll('.custom-dropdown-container.is-open').forEach(c => {
        if (c !== container) c.classList.remove('is-open', 'open-up');
      });

      // Check viewport position to decide whether to animate UP or DOWN
      const rect = trigger.getBoundingClientRect();
      const spaceBelow = window.innerHeight - rect.bottom;
      const spaceAbove = rect.top;

      if (spaceBelow < 260 && spaceAbove > spaceBelow) {
        container.classList.add('open-up');
      } else {
        container.classList.remove('open-up');
      }

      container.classList.add('is-open');
    }

    function closeDropdown() {
      container.classList.remove('is-open');
    }

    trigger.addEventListener('click', (e) => {
      e.stopPropagation();
      if (container.classList.contains('is-open')) {
        closeDropdown();
      } else {
        openDropdown();
      }
    });

    // Keyboard support
    trigger.addEventListener('keydown', (e) => {
      if (e.key === 'ArrowDown' || e.key === 'Enter' || e.key === ' ') {
        e.preventDefault();
        if (!container.classList.contains('is-open')) {
          openDropdown();
        }
      } else if (e.key === 'Escape') {
        closeDropdown();
      }
    });

    // Listen to changes on native select (e.g. from Django related widget wrapper popup)
    select.addEventListener('change', () => {
      renderOptions();
    });

    if (window.django && window.django.jQuery) {
      window.django.jQuery(select).on('change', () => {
        renderOptions();
      });
    }

    // Observe changes to options (e.g. Added, removed, or edited via Django popups)
    if (typeof MutationObserver !== 'undefined') {
      const selectObserver = new MutationObserver(() => {
        renderOptions();
      });
      selectObserver.observe(select, { childList: true, subtree: true, characterData: true });
    }

    // Assemble
    renderOptions();
    container.appendChild(trigger);
    container.appendChild(menu);

    select.parentNode.insertBefore(container, select.nextSibling);
  }

  // Global click outside to close
  document.addEventListener('click', (e) => {
    if (!e.target.closest('.custom-dropdown-container')) {
      document.querySelectorAll('.custom-dropdown-container.is-open').forEach(c => {
        c.classList.remove('is-open', 'open-up');
      });
    }
  });

  // Global Escape key
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
      document.querySelectorAll('.custom-dropdown-container.is-open').forEach(c => {
        c.classList.remove('is-open', 'open-up');
      });
    }
  });

  // Intercept disabled related-widget links in capture phase before app.js tries new URL(link.href)
  document.addEventListener(
    'click',
    (event) => {
      const link = event.target.closest('a.related-widget-wrapper-link');
      if (!link) return;

      // Close 3-dots dropdown menu immediately upon choosing an option
      document.querySelectorAll('[x-data*="openRelatedWidgetWrapper"]').forEach(el => {
        if (window.Alpine && Alpine.$data(el)) {
          Alpine.$data(el).openRelatedWidgetWrapper = false;
        }
      });

      if (!link.getAttribute('href') || link.getAttribute('aria-disabled') === 'true') {
        event.preventDefault();
        event.stopImmediatePropagation();
      }
    },
    { capture: true }
  );

  function initAllSelects() {
    // Target selects on forms
    const selects = document.querySelectorAll('form select:not([data-custom-dropdown-initialized]):not([multiple])');
    selects.forEach(initSelect);
  }

  function setupBodyObserver() {
    if (typeof MutationObserver !== 'undefined' && document.body) {
      new MutationObserver(initAllSelects).observe(document.body, { childList: true, subtree: true });
    }
  }

  // Handle table individual filter dropdown changes
  function applyFilterChange(name, value) {
    if (!name) return;
    const url = new URL(window.location.href);
    if (value !== '' && value !== undefined && value !== null) {
      url.searchParams.set(name, value);
    } else {
      url.searchParams.delete(name);
    }
    url.searchParams.delete('p');
    window.location.href = url.toString();
  }

  document.addEventListener('change', (e) => {
    const dropdown = e.target.closest('.filter-item-dropdown');
    if (!dropdown) return;
    if (e.target.matches('select, input[type="radio"]')) {
      applyFilterChange(e.target.name, e.target.value);
    }
  });

  function highlightActiveFilterButtons() {
    document.querySelectorAll('.filter-item-dropdown').forEach(dropdown => {
      const activeDateLi = dropdown.querySelector('.filter-spec-content li.text-primary-600:not(:has(a[href="?"]))');
      const activeLink = dropdown.querySelector('.filter-spec-content a.active:not([href$="?"]):not([href$="?="])');
      const activeRadio = dropdown.querySelector('input[type="radio"]:checked:not([value=""])');
      const activeSelect = dropdown.querySelector('select');
      const hasSelectVal = activeSelect && activeSelect.value !== '';

        if (activeDateLi || activeLink || activeRadio || hasSelectVal) {
          const btn = dropdown.querySelector('.filter-button');
          if (btn) {
            btn.classList.add(
              '!bg-primary-50',
              '!border-primary-400',
              '!text-primary-700',
              'dark:!bg-primary-950/40',
              'dark:!border-primary-600',
              'dark:!text-primary-300',
              'font-semibold'
            );
          }
        }
      });
  }

  function setupSelect2FilterListener() {
    if (window.django && window.django.jQuery) {
      window.django.jQuery(document).on('select2:select select2:clear', '.filter-item-dropdown select', function (e) {
        applyFilterChange(this.name, this.value);
      });
    } else {
      setTimeout(setupSelect2FilterListener, 200);
    }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
      initAllSelects();
      setupBodyObserver();
      highlightActiveFilterButtons();
      setupSelect2FilterListener();
    });
  } else {
    initAllSelects();
    setupBodyObserver();
    highlightActiveFilterButtons();
    setupSelect2FilterListener();
  }
})();

