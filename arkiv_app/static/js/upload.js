document.addEventListener('DOMContentLoaded', () => {
  const form = document.querySelector('#upload-form');
  if (!form) return;
  const input = form.querySelector('input[type="file"]');
  const area = document.querySelector('#upload-area');
  const preview = document.querySelector('#preview');
  const progressBar = form.querySelector('.progress-bar');
  const progressWrap = form.querySelector('.progress');

  const showPreviews = (files) => {
    if (!preview) return;
    preview.innerHTML = '';
    Array.from(files).forEach(file => {
      const reader = new FileReader();
      reader.onload = (ev) => {
        const img = document.createElement('img');
        img.src = ev.target.result;
        preview.appendChild(img);
      };
      reader.readAsDataURL(file);
    });
  };

  area.addEventListener('click', () => input.click());
  area.addEventListener('dragover', (e) => {
    e.preventDefault();
    area.classList.add('dragover');
  });
  area.addEventListener('dragleave', () => {
    area.classList.remove('dragover');
  });
  area.addEventListener('drop', (e) => {
    e.preventDefault();
    area.classList.remove('dragover');
    input.files = e.dataTransfer.files;
    showPreviews(input.files);
  });
  input.addEventListener('change', () => showPreviews(input.files));

  form.addEventListener('submit', (e) => {
    if (!progressBar) return;
    e.preventDefault();
    progressWrap.classList.remove('d-none');
    const xhr = new XMLHttpRequest();
    xhr.open('POST', form.action);
    xhr.upload.addEventListener('progress', (ev) => {
      if (ev.lengthComputable) {
        const pct = Math.round((ev.loaded / ev.total) * 100);
        progressBar.style.width = pct + '%';
        progressBar.textContent = pct + '%';
      }
    });
    xhr.onload = () => {
      if (xhr.status >= 200 && xhr.status < 300) {
        location.reload();
      } else {
        alert('Erro ao enviar arquivo');
      }
    };
    const formData = new FormData(form);
    xhr.send(formData);
  });
});
