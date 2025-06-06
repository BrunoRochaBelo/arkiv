// Seleção simples em galerias de assets
document.addEventListener('click', function(e){
  const item = e.target.closest('.asset-item-selectable');
  if(item && e.target.matches('input[type="checkbox"]')){
    item.classList.toggle('selected', e.target.checked);
  }
});

// Placeholder para infinite scroll
const sentinel = document.querySelector('[data-gallery-sentinel]');
if(sentinel){
  const observer = new IntersectionObserver((entries)=>{
    if(entries[0].isIntersecting){
      const event = new CustomEvent('gallery:loadMore');
      document.dispatchEvent(event);
    }
  });
  observer.observe(sentinel);
}
