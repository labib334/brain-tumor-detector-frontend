// script.js
// Set API_BASE to your backend URL once deployed on Render.
// During local dev you can leave as localhost, but when live use https://your-service.onrender.com
const API_BASE = "https://brain-tumor-backend-8h91.onrender.com/";
// change this later to your Render URL, e.g. "https://my-backend.onrender.com"

const input = document.getElementById('file-input')
const preview = document.getElementById('preview')
const submit = document.getElementById('submit')
const results = document.getElementById('results')
let file = null

input.addEventListener('change', e => {
  file = e.target.files[0]
  if (!file) return
  preview.src = URL.createObjectURL(file)
  preview.style.display = 'block'
})

submit.addEventListener('click', async () => {
  if (!file) { alert('Choose a file'); return }
  results.textContent = 'Analyzing...'
  const fd = new FormData()
  fd.append('file', file)
  try {
    const r = await fetch(`${API_BASE}/predict`, {
      method: 'POST',
      body: fd
    })
    if (!r.ok) {
      const txt = await r.text()
      results.textContent = `Server error: ${r.status} - ${txt}`
      return
    }
    const data = await r.json()
    results.textContent = JSON.stringify(data, null, 2)
  } catch (err) {
    results.textContent = `Network error: ${err.message}`
  }
})
