document.addEventListener('DOMContentLoaded', () => {

  document.querySelectorAll('.toast').forEach((el) => {
    const remove = () => el.remove();
    const timer = setTimeout(() => {
      el.classList.add('toast-removing');
      setTimeout(remove, 300);
    }, 4000);
    const btn = el.querySelector('button');
    if (btn) btn.addEventListener('click', () => {
      clearTimeout(timer);
      el.classList.add('toast-removing');
      setTimeout(remove, 300);
    });
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

    if ((ev.ctrlKey || ev.metaKey) && ev.key.toLowerCase() === 'k') {
      ev.preventDefault();
      const input = document.querySelector('#globalSearchInput');
      if (input) input.focus();
    }
  });

  document.querySelectorAll('.btn-logout').forEach((btn) => {
    btn.addEventListener('click', (ev) => {
      if (!confirm('Tem certeza que deseja sair?')) {
        ev.preventDefault();
      }
    });
  });
});
