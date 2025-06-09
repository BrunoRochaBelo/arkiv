// Script simples para o modal de usuário
document.addEventListener('DOMContentLoaded', () => {
  const avatar = document.querySelector('#avatarTrigger'); // botão que abre
  const modal = document.getElementById('profileModal'); // contêiner do modal
  if (!avatar || !modal) return;
  const closeBtn = modal.querySelector('.profile-modal-close');

  const dialog = modal.querySelector('.profile-modal');

  const openModal = () => {
    modal.removeAttribute('hidden');
    modal.classList.add('open');
    dialog.focus();
  };

  const closeModal = () => {
    modal.classList.remove('open');
    modal.setAttribute('hidden', '');
    avatar.focus();
  };

  // abre ao clicar no avatar
  avatar.addEventListener('click', openModal);
  avatar.addEventListener('keydown', (ev) => {
    if (ev.key === 'Enter' || ev.key === ' ') {
      ev.preventDefault();
      openModal();
    }
  });
  // fecha no botão de fechar
  closeBtn?.addEventListener('click', closeModal);

  // fecha ao clicar fora do box principal
  modal.addEventListener('click', (ev) => {
    if (ev.target === modal) closeModal();
  });

  document.addEventListener('keydown', (ev) => {
    if (ev.key === 'Escape' && !modal.hasAttribute('hidden')) {
      closeModal();
    }
  });
});
