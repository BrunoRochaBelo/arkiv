function initGlobalSearch() {
  const input = document.querySelector('#globalSearchInput');
  const resultsEl = document.querySelector('#results');
  const noResultsEl = document.querySelector('#noResults');
  const filtersForm = document.querySelector('#filtersForm');
  const clearBtn = document.querySelector('#clearSearch');

  if (!input || !resultsEl || !filtersForm) return;

  function fetchResults() {
    const params = new URLSearchParams(new FormData(filtersForm));
    if (input.value.trim()) params.set('q', input.value.trim());
    fetch('/api/search?' + params.toString())
      .then(r => r.json())
      .then(data => {
        resultsEl.innerHTML = '';
        if (!data.data || data.data.length === 0) {
          noResultsEl.classList.remove('d-none');
          return;
        }
        noResultsEl.classList.add('d-none');
        data.data.forEach(item => {
          const col = document.createElement('div');
          col.className = 'col-12 col-md-6 col-lg-4';
          col.innerHTML = `
            <div class="card search-result shadow-sm h-100">
              <div class="card-body">
                <div class="fw-semibold mb-1">${item.name}</div>
                <small class="text-muted text-capitalize">${item.type}</small>
              </div>
            </div>`;
          resultsEl.appendChild(col);
        });
      });
  }

  input.addEventListener('input', fetchResults);
  filtersForm.addEventListener('change', fetchResults);
  clearBtn.addEventListener('click', () => {
    input.value = '';
    fetchResults();
    input.focus();
  });

  fetchResults();
}

if (document.readyState !== 'loading') {
  initGlobalSearch();
} else {
  document.addEventListener('DOMContentLoaded', initGlobalSearch);
}
