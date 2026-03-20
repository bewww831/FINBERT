// ── WEIGHT DONUT CHART ───────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  const ctx = document.getElementById('weightChart').getContext('2d')
  new Chart(ctx, {
    type: 'doughnut',
    data: {
      labels: ['XGBoost', 'FinBERT', 'ResNet-18'],
      datasets: [{
        data: [52.5, 32.5, 15],
        backgroundColor: ['#00c2ff', '#a78bfa', '#34d399'],
        borderWidth: 0,
        hoverOffset: 6
      }]
    },
    options: {
      cutout: '68%',
      plugins: {
        legend: { display: false },
        tooltip: {
          callbacks: {
            label: ctx => ` ${ctx.label}: ${ctx.parsed}%`
          }
        }
      },
      animation: { animateRotate: true, duration: 900 }
    }
  })
})