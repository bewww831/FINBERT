async function runPrediction() {
  const ticker = document.getElementById("tickerInput").value.trim().toUpperCase()
  if (!ticker) return

  const btn = document.getElementById("predictBtn")
  btn.disabled = true
  btn.textContent = "Running…"
  document.getElementById("loading").style.display  = "flex"
  document.getElementById("error").style.display    = "none"
  document.getElementById("results").style.display  = "none"

  try {
    const res  = await fetch("http://localhost:8000/predict", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ ticker })
    })
    const data = await res.json()
    if (data.error) throw new Error(data.error)

    const ts   = data.timeseries
    const sent = data.sentiment
    const cnn  = data.cnn
    const dec  = data.decision

    // ── Verdict card ─────────────────────────────────────
    document.getElementById("tickerLabel").textContent = data.ticker
    const recEl = document.getElementById("finalRec")
    recEl.textContent = dec.emoji + " " + dec.recommendation
    recEl.className = "verdict-rec " + (
      dec.recommendation.includes("BUY")  ? "buy"  :
      dec.recommendation.includes("SELL") ? "sell" : "hold"
    )
    document.getElementById("finalScore").textContent       = "Final Score: " + dec.final_score
    document.getElementById("finalExplanation").textContent = dec.explanation

    // ── Time Series ───────────────────────────────────────
    const tsColor = ts.label === "buy" ? "buy" : ts.label === "sell" ? "sell" : "hold"
    document.getElementById("tsLabel").textContent   = ts.label.toUpperCase()
    document.getElementById("tsLabel").className     = "model-label " + tsColor
    document.getElementById("tsBuy").textContent     = (ts.buy  * 100).toFixed(2) + "%"
    document.getElementById("tsHold").textContent    = (ts.hold * 100).toFixed(2) + "%"
    document.getElementById("tsSell").textContent    = (ts.sell * 100).toFixed(2) + "%"
    document.getElementById("tsBuyBar").style.width  = (ts.buy  * 100) + "%"
    document.getElementById("tsHoldBar").style.width = (ts.hold * 100) + "%"
    document.getElementById("tsSellBar").style.width = (ts.sell * 100) + "%"
    document.getElementById("tsScore").textContent   = dec.ts_score

    // ── Sentiment ─────────────────────────────────────────
    const sColor = sent.label === "positive" ? "buy" : sent.label === "negative" ? "sell" : "hold"
    document.getElementById("sentLabel").textContent   = sent.label.toUpperCase()
    document.getElementById("sentLabel").className     = "model-label " + sColor
    document.getElementById("sentPos").textContent     = (sent.positive * 100).toFixed(2) + "%"
    document.getElementById("sentNeu").textContent     = (sent.neutral  * 100).toFixed(2) + "%"
    document.getElementById("sentNeg").textContent     = (sent.negative * 100).toFixed(2) + "%"
    document.getElementById("sentPosBar").style.width  = (sent.positive * 100) + "%"
    document.getElementById("sentNeuBar").style.width  = (sent.neutral  * 100) + "%"
    document.getElementById("sentNegBar").style.width  = (sent.negative * 100) + "%"
    document.getElementById("sentScore").textContent   = dec.sent_score
    document.getElementById("sentHeadline").textContent = "📰 " + sent.headline

    // ── CNN ───────────────────────────────────────────────
    const cColor = cnn.label === "bullish" ? "buy" : cnn.label === "bearish" ? "sell" : "hold"
    document.getElementById("cnnLabel").textContent    = cnn.label.toUpperCase()
    document.getElementById("cnnLabel").className      = "model-label " + cColor
    document.getElementById("cnnBull").textContent     = (cnn.bullish * 100).toFixed(2) + "%"
    document.getElementById("cnnNeu").textContent      = (cnn.neutral * 100).toFixed(2) + "%"
    document.getElementById("cnnBear").textContent     = (cnn.bearish * 100).toFixed(2) + "%"
    document.getElementById("cnnBullBar").style.width  = (cnn.bullish * 100) + "%"
    document.getElementById("cnnNeuBar").style.width   = (cnn.neutral * 100) + "%"
    document.getElementById("cnnBearBar").style.width  = (cnn.bearish * 100) + "%"
    document.getElementById("cnnScore").textContent    = dec.cnn_score

    // ── Contributions ─────────────────────────────────────
    document.getElementById("tsFormula").textContent   = `0.525 × ${dec.ts_score} =`
    document.getElementById("sentFormula").textContent = `0.325 × ${dec.sent_score} =`
    document.getElementById("cnnFormula").textContent  = `0.150 × ${dec.cnn_score} =`
    document.getElementById("tsContrib").textContent   = dec.ts_contrib
    document.getElementById("sentContrib").textContent = dec.sent_contrib
    document.getElementById("cnnContrib").textContent  = dec.cnn_contrib
    document.getElementById("finalScoreBottom").textContent = dec.final_score

    // ── News ──────────────────────────────────────────────
    const newsList = document.getElementById("newsList")
    newsList.innerHTML = ""
    sent.articles.forEach(article => {
      const labelColor = article.label === "positive" ? "#22c55e"
                       : article.label === "negative" ? "#ef4444"
                       : "#f59e0b"
      const headlineHtml = article.url
        ? `<a href="${article.url}" target="_blank" rel="noopener noreferrer" class="news-title-text">${article.headline}</a>`
        : `<div class="news-title-text">${article.headline}</div>`

      newsList.innerHTML += `
        <div class="news-item">
          <div class="news-top">
            <div>
              ${headlineHtml}
              <div class="news-source">${article.source}</div>
              <div class="news-summary">${article.summary}</div>
            </div>
            <div class="news-badge">
              <div class="news-label" style="color:${labelColor}">${article.label.toUpperCase()}</div>
              <span class="news-conf">${article.conf}% Conf.</span>
            </div>
          </div>
        </div>
      `
    })

    document.getElementById("results").style.display = "block"

  } catch (err) {
    document.getElementById("error").style.display = "block"
    document.getElementById("error").textContent   = "❌ " + err.message
  } finally {
    document.getElementById("loading").style.display = "none"
    btn.disabled    = false
    btn.textContent = "Analyse"
  }
}

document.addEventListener("DOMContentLoaded", () => {
  document.getElementById("tickerInput").addEventListener("keypress", e => {
    if (e.key === "Enter") runPrediction()
  })
})

// ── APPLY DISPLAY SETTINGS ON DASHBOARD ─────────────────────────────────────
function applyDashboardSettings() {
  try {
    const stored = localStorage.getItem("finlens_settings")
    const s = stored ? JSON.parse(stored) : {}

    const showWeights   = s.showWeights   !== false
    const showNews      = s.showNews      !== false
    const showScores    = s.showScores    !== false
    const compactLayout = s.compactLayout === true

    // show/hide weights card
    const wCard = document.querySelector(".weights-card")
    if (wCard) wCard.style.display = showWeights ? "" : "none"

    // show/hide news card
    const nCard = document.querySelector(".news-card")
    if (nCard) nCard.style.display = showNews ? "" : "none"

    // show/hide normalised score rows inside model cards
    document.querySelectorAll(".model-score-row").forEach(el => {
      el.style.display = showScores ? "" : "none"
    })

    // compact layout
    document.body.classList.toggle("compact", compactLayout)
  } catch {}
}

document.addEventListener("DOMContentLoaded", applyDashboardSettings)

// ── LIVE NAVBAR TICKER ────────────────────────────────────────────────────────

async function loadNavTicker() {
  const track = document.getElementById("tickerTrack")
  if (!track) return
  try {
    const res  = await fetch("http://localhost:8000/prices")
    const data = await res.json()
    if (!data.prices || data.prices.length === 0) return

    const text = data.prices.map(p => {
      const sign  = p.change >= 0 ? "▲" : "▼"
      const color = p.change >= 0 ? "#22c55e" : "#ef4444"
      return `<span style="color:#e2e8f0;font-weight:700">${p.ticker}</span> ` +
             `<span style="color:#94a3b8">$${p.price.toFixed(2)}</span> ` +
             `<span style="color:${color}">${sign}${Math.abs(p.change).toFixed(2)}%</span>`
    }).join("&nbsp;&nbsp;&nbsp;·&nbsp;&nbsp;&nbsp;")

    // duplicate for seamless loop
    track.innerHTML = text + "&nbsp;&nbsp;&nbsp;·&nbsp;&nbsp;&nbsp;" + text

  } catch {
    // silently keep the fallback text already in the HTML
  }
}

document.addEventListener("DOMContentLoaded", () => {
  loadNavTicker()
  setInterval(loadNavTicker, 60_000)   // refresh every 60 s
})