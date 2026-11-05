/**
 * Auto-dismissing error messages, field errors, and confirmation alerts
 * Fades out and smoothly collapses field errors and success/info messages after a few seconds,
 * or immediately when the user starts interacting with the input field.
 */
(function () {
  // Only execute within the Django admin area (/admin/)
  if (!window.location.pathname.startsWith('/admin')) {
    return;
  }

  const DISMISS_DELAY_MS = 4000; // 4 seconds

  function getFieldErrors() {
    const targets = [];

    // 1. Unfold error message wrappers containing ul.errorlist
    document.querySelectorAll('.field-line .mt-2.text-red-600, .field-line .mt-2.text-red-500, .form-field .mt-2.text-red-600, .form-field .mt-2.text-red-500').forEach(el => {
      targets.push(el);
    });

    // 2. Standalone ul.errorlist that wasn't already matched
    document.querySelectorAll('ul.errorlist').forEach(el => {
      const parent = el.closest('.mt-2.text-red-600, .mt-2.text-red-500');
      if (parent) {
        if (!targets.includes(parent)) targets.push(parent);
      } else if (!targets.includes(el)) {
        targets.push(el);
      }
    });

    // 3. Frontend field error paragraphs (e.g. appointment_form.html)
    document.querySelectorAll('.field-error-message, form p.text-red-700').forEach(el => {
      if (!targets.includes(el)) targets.push(el);
    });

    return targets;
  }

  function getConfirmationMessages() {
    const targets = [];

    // 1. Unfold flash messages in admin base
    document.querySelectorAll('ul.flex.flex-col.gap-3.mb-4 > li, .message-success, .message-info, .message-warning').forEach(el => {
      const target = el.closest('li') || el;
      if (!targets.includes(target)) targets.push(target);
    });

      // 2. Standard Django flash messagelist and explicit alert boxes
      document.querySelectorAll('ul.messagelist > li, .messagelist .success, .messagelist .info, .messagelist .warning, [data-flash-message], .flash-message').forEach(el => {
        const target = el.closest('li') || el;
        if (!targets.includes(target)) targets.push(target);
      });

      return targets;
    }

  function dismissElement(el, removeErrorClass) {
        if (!el || el.dataset.dismissing === 'true') return;

        // Never auto-dismiss status badges, tags, pills, or data content
        if (el.matches('.rounded-full, .badge, [data-status-badge], [data-status-tag]') ||
          el.closest('.rounded-full, .badge')) {
          return;
        }
        el.dataset.dismissing = 'true';
        el.classList.add('error-dismiss-target');

        // Freeze height for smooth CSS transition
        el.style.maxHeight = el.scrollHeight + 'px';
        el.style.opacity = '1';

        // Force browser reflow
        void el.offsetHeight;

        setTimeout(() => {
          el.classList.add('error-dismissing');

          setTimeout(() => {
            if (removeErrorClass) {
              const fieldParent = el.closest('.errors, .field-line, .form-field');
              if (fieldParent) {
                fieldParent.classList.remove('errors');
                fieldParent.querySelectorAll('[aria-invalid="true"]').forEach(input => {
                  input.setAttribute('aria-invalid', 'false');
                });
              }
            }

            // Check if all field errors are gone; if so, dismiss top errornote
            const remainingErrors = document.querySelectorAll(
              '.field-line .mt-2.text-red-600:not(.error-dismissing), .field-line .mt-2.text-red-500:not(.error-dismissing), ul.errorlist:not(.error-dismissing), .field-error-message:not(.error-dismissing)'
            );
            if (remainingErrors.length === 0) {
              document.querySelectorAll('.errornote, #login-error-alert').forEach(note => {
                dismissElement(note, false);
              });
            }

            const parentUl = el.closest('ul.flex.flex-col.gap-3.mb-4');
            if (el.parentNode) {
              el.parentNode.removeChild(el);
            }
            if (parentUl && (parentUl.children.length === 0 || Array.from(parentUl.children).every(c => c.style.display === 'none'))) {
              parentUl.style.display = 'none';
            }
          }, 450);
        }, 40);
      }

  function initAutoDismiss() {
        const fieldErrors = getFieldErrors();
        const errorNotes = document.querySelectorAll('.errornote');
        const confirmationMessages = getConfirmationMessages();

        if (fieldErrors.length === 0 && errorNotes.length === 0 && confirmationMessages.length === 0) return;

        // Automatically dismiss after delay
        setTimeout(() => {
          fieldErrors.forEach(err => dismissElement(err, true));
          errorNotes.forEach(note => dismissElement(note, false));
          confirmationMessages.forEach(msg => dismissElement(msg, false));
        }, DISMISS_DELAY_MS);

        // Also dismiss field error immediately when user types in or changes that field
        document.querySelectorAll('input, select, textarea').forEach(input => {
          const handler = () => {
            const fieldParent = input.closest('.errors, .field-line, .form-field');
            if (fieldParent) {
              fieldParent.querySelectorAll(
                '.mt-2.text-red-600, .mt-2.text-red-500, ul.errorlist, .field-error-message, p.text-red-700'
              ).forEach(err => dismissElement(err, true));
            }
          };
          input.addEventListener('input', handler, { passive: true });
          input.addEventListener('change', handler, { passive: true });
        });
      }

  if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', initAutoDismiss);
    } else {
      initAutoDismiss();
    }
  }) ();
