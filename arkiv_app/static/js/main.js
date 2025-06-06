const STORAGE_KEY = 'arkiv_theme';

function applyTheme(theme) {
  document.documentElement.setAttribute('data-theme', theme);
  localStorage.setItem(STORAGE_KEY, theme);
  const toggleBtn = document.getElementById('themeToggle');
  if (toggleBtn) {
    toggleBtn.innerHTML = theme === 'dark'
      ? '<i class="bi bi-sun-fill"></i>'
      : '<i class="bi bi-moon-fill"></i>';
  }
}

function toggleTheme() {
  const current = document.documentElement.getAttribute('data-theme');
  const next = current === 'dark' ? 'light' : 'dark';
  applyTheme(next);
}

document.addEventListener('DOMContentLoaded', () => {
  const saved = localStorage.getItem(STORAGE_KEY) || 'light';
  applyTheme(saved);

  document.querySelectorAll('.flash-item').forEach((el) => {
    setTimeout(() => el.remove(), 5000);
  });

  const forms = document.querySelectorAll('.guarded-form');
  forms.forEach((form) => {
    const submit = form.querySelector('[type="submit"]');
    if (submit) submit.disabled = true;
    const initial = new FormData(form);
    const check = () => {
      const current = new FormData(form);
      let changed = false;
      for (const [k, v] of current.entries()) {
        if (initial.get(k) !== v) {
          changed = true;
          break;
        }
      }
      const requiredFilled = Array.from(form.querySelectorAll('[required]')).every((el) => el.value.trim() !== '');
      if (submit) submit.disabled = !(changed && requiredFilled);
    };
    form.addEventListener('input', check);
    form.addEventListener('change', check);
  });

  document.addEventListener('keydown', (ev) => {
    if (ev.key === 'Escape') {
      const cancel = document.querySelector('.btn-cancel');
      if (cancel) cancel.click();
    }
  });
});
