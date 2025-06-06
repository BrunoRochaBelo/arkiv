 document.addEventListener('DOMContentLoaded', () => {
   const modalEl = document.getElementById('userModal');
   if (!modalEl) return;
   const bsModal = new bootstrap.Modal(modalEl);
   document.querySelectorAll('[data-bs-target="#userModal"]').forEach((el) => {
     el.addEventListener('click', (ev) => {
       ev.preventDefault();
       if (!modalEl.classList.contains('show')) {
         bsModal.show();
       }
     });
   });
 });
