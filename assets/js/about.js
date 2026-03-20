// ── SERVER STATUS ─────────────────────────────────────────────
async function checkServerStatus() {
  const el = document.getElementById('serverStatus')
  if (!el) return
  try {
    const res = await fetch('http://localhost:8000/health', { signal: AbortSignal.timeout(4000) })
    if (res.ok) {
      el.innerHTML = '<span class="status-dot status-ok"></span> Online'
    } else {
      el.innerHTML = '<span class="status-dot status-error"></span> Error'
    }
  } catch {
    el.innerHTML = '<span class="status-dot status-error"></span> Offline'
  }
}

// ── INIT ──────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  checkServerStatus()
})