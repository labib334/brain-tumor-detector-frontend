// script.js
// IMPORTANT: no trailing slash in API_BASE
const API_BASE = "https://brain-tumor-backend-8h91.onrender.com";

const input = document.getElementById('file-input');
const preview = document.getElementById('preview');
const submit = document.getElementById('submit');
const results = document.getElementById('results');
let file = null;

input.addEventListener('change', e => {
  file = e.target.files[0];
  if (!file) return;
  preview.src = URL.createObjectURL(file);
  preview.style.display = 'block';
});

submit.addEventListener('click', async () => {
  if (!file) { alert('Choose a file'); return; }
  results.textContent = 'Analyzing...';

  const fd = new FormData();
  fd.append('file', file);

  try {
    const url = `${API_BASE}/predict`; // API_BASE has no trailing slash
    const r = await fetch(url, {
      method: 'POST',
      body: fd
    });

    if (!r.ok) {
      const txt = await r.text().catch(()=>'<no body>');
      results.textContent = `Server error: ${r.status} - ${txt}`;
      return;
    }

    const ct = r.headers.get('content-type') || '';
    if (ct.includes('application/json')) {
      const data = await r.json();
      results.textContent = JSON.stringify(data, null, 2);
    } else {
      const txt = await r.text();
      results.textContent = `Server response (non-json): ${txt}`;
    }
  } catch (err) {
    results.textContent = `Network error: ${err.message}`;
    console.error('Fetch error:', err);
  }
});
