document.addEventListener('DOMContentLoaded', () => {
  const form = document.getElementById('search-form');
  const input = document.getElementById('search-input');
  const typeSelect = document.getElementById('search-type');
  const multiKeyCheckbox = document.getElementById('multi-key');
  const resultsContainer = document.getElementById('results');
  const clearBtn = document.getElementById('clearBtn');

  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const query = input.value.trim();
    const searchType = typeSelect.value;
    const multiKey = multiKeyCheckbox.checked;

    resultsContainer.innerHTML = '<div class="text-muted">Searching...</div>';
    try {
      const res = await fetch('/search', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query, searchType, multiKey })
      });
      const data = await res.json();
      if (data.error) {
        resultsContainer.innerHTML = `<div class="text-danger">${data.error}</div>`;
        return;
      }
      const hits = data.results || [];
      if (hits.length === 0) {
        resultsContainer.innerHTML = `<div class="text-warning">No results found.</div>`;
        return;
      }
      // Render as Bootstrap list-group
      const list = document.createElement('div');
      list.className = 'list-group';
      hits.forEach(item => {
        const a = document.createElement('a');
        a.className = 'list-group-item list-group-item-action flex-column align-items-start';
        a.href = '#';
        a.innerHTML = `
          <div class="d-flex w-100 justify-content-between">
            <h5 class="mb-1">${item.title}</h5>
            <small>Score: ${item.score.toFixed(2)}</small>
          </div>
          <p class="mb-1">Composer: ${item.composer}</p>
        `;
        list.appendChild(a);
      });
      resultsContainer.innerHTML = '';
      resultsContainer.appendChild(list);
    } catch (err) {
      resultsContainer.innerHTML = `<div class="text-danger">Error: ${err.message}</div>`;
    }
  });

  clearBtn.addEventListener('click', () => {
    input.value = '';
    typeSelect.value = 'phrase';
    multiKeyCheckbox.checked = false;
    resultsContainer.innerHTML = '';
  });
});