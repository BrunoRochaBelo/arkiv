document.addEventListener('DOMContentLoaded', () => {
  const modalEl = document.getElementById('userModal');
  if (!modalEl) return;
  document.querySelectorAll('[data-bs-target="#userModal"]').forEach((el) => {
    el.addEventListener('click', (ev) => {
      ev.preventDefault();
      const bsModal = bootstrap.Modal.getOrCreateInstance(modalEl);
      bsModal.show();
    });
  });
});
