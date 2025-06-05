function applyTheme(theme) {
  document.documentElement.setAttribute('data-theme', theme);
  localStorage.setItem('theme', theme);
  const toggleBtn = document.querySelector('.theme-toggle');
  if (toggleBtn) {
    toggleBtn.textContent = theme === 'dark' ? '☀️' : '🌙';
  }
}

function toggleTheme() {
  const current = document.documentElement.getAttribute('data-theme');
  const next = current === 'dark' ? 'light' : 'dark';
  applyTheme(next);
}

document.addEventListener('DOMContentLoaded', () => {
  const saved = localStorage.getItem('theme') || 'light';
  applyTheme(saved);

  document.querySelectorAll('.flash li').forEach((item) => {
    const btn = document.createElement('button');
    btn.className = 'close-btn';
    btn.innerHTML = '&times;';
    btn.addEventListener('click', () => item.remove());
    item.appendChild(btn);
    setTimeout(() => item.remove(), 5000);
  });
});
