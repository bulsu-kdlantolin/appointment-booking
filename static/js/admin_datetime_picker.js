/**
 * Admin Date & Time Picker using Flatpickr
 * Unifies Django Admin with the public frontend appointment booking UI design.
 */
(function () {
  'use strict';

  function initPickers() {
    if (typeof flatpickr === 'undefined') {
      setTimeout(initPickers, 50);
      return;
    }

    // 1. Initialize Date Pickers (only original visible inputs without flatpickr-input)
    const dateInputs = document.querySelectorAll('input.vDateField:not(.flatpickr-input):not([type="hidden"])');
    dateInputs.forEach((input) => {
      // Block off all past dates unconditionally for both adding and editing
      const fp = flatpickr(input, {
        dateFormat: 'Y-m-d',
        monthSelectorType: 'static',
        minDate: 'today',
        disableMobile: true,
        allowInput: false,
      });
      fp._positionElement = fp.input;
    });

    // Ensure any previously initialized date fields enforce minDate: today
    document.querySelectorAll('input.vDateField').forEach((input) => {
      if (input._flatpickr) {
        input._flatpickr.set('minDate', 'today');
      }
    });

    // 2. Initialize Time Pickers (only original visible inputs without flatpickr-input)
    const timeInputs = document.querySelectorAll('input.vTimeField:not(.flatpickr-input):not([type="hidden"])');
    timeInputs.forEach((input) => {
      const fp = flatpickr(input, {
        noCalendar: true,
        enableTime: true,
        dateFormat: 'H:i:S',
        altInput: true,
        altFormat: 'h:i K',
        minuteIncrement: 30,
        time_24hr: false,
        disableMobile: true,
        allowInput: true,
      });

      if (fp.altInput) {
        fp._positionElement = fp.altInput;
      }
    });
  }

  // Intercept calendar & clock clicks in capture phase
  document.addEventListener(
    'click',
    function (e) {
      const calBtn = e.target.closest('#calendarlink0, [id^="calendarlink"], .date-icon');
      if (calBtn) {
        e.preventDefault();
        e.stopPropagation();
        e.stopImmediatePropagation();

        const container = calBtn.closest('.datetime') || calBtn.closest('.relative') || calBtn.parentElement;
        const input = container
          ? container.querySelector('input.vDateField')
          : document.querySelector('input.vDateField');

        if (input && input._flatpickr) {
          const fp = input._flatpickr;
          fp.open(null, fp.altInput || fp.input);
        }
        return false;
      }

      const clockBtn = e.target.closest('#clocklink0, [id^="clocklink"], .clock-icon');
      if (clockBtn) {
        e.preventDefault();
        e.stopPropagation();
        e.stopImmediatePropagation();

        const container = clockBtn.closest('.datetime') || clockBtn.closest('.relative') || clockBtn.parentElement;
        const input = container
          ? container.querySelector('input.vTimeField')
          : document.querySelector('input.vTimeField');

        if (input && input._flatpickr) {
          const fp = input._flatpickr;
          fp.open(null, fp.altInput || fp.input);
        }
        return false;
      }
    },
    true
  );

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initPickers);
  } else {
    initPickers();
  }
})();
