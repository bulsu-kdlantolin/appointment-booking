/**
 * Ensures Light mode is the default theme in the Unfold admin dashboard
 * when the user has not explicitly chosen a preference yet.
 */
(function () {
  try {
    const current = localStorage.getItem('adminTheme');
    if (current === null || current === '"auto"' || current === 'auto') {
      localStorage.setItem('adminTheme', JSON.stringify('light'));
    }
  } catch (e) {
    // localStorage not accessible
  }
})();
