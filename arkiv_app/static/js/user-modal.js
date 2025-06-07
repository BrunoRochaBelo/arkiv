// Script simples para o modal de usuário
document.addEventListener('DOMContentLoaded', () => {
  const avatar = document.querySelector('#avatarTrigger'); // botão que abre
  const modal = document.getElementById('profileModal'); // contêiner do modal
  if (!avatar || !modal) return;
  const closeBtn = modal.querySelector('.profile-modal-close');

  const openModal = () => {
    modal.removeAttribute('hidden');
    modal.classList.add('open');
  };

  const closeModal = () => {
    modal.classList.remove('open');
    modal.setAttribute('hidden', '');
  };

  // abre ao clicar no avatar
  avatar.addEventListener('click', openModal);
  // fecha no botão de fechar
  closeBtn?.addEventListener('click', closeModal);

  // fecha ao clicar fora do box principal
  modal.addEventListener('click', (ev) => {
    if (ev.target === modal) closeModal();
  });
});
