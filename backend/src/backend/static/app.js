// All egen JavaScript for siden (AD-8). Tegner grafen fra JSON-blokken
// `#grafdata`, som lages fra samme Dataserie som tabellen. Tekstene og
// tallene kommer fra malen. Fargene kommer fra CSS-variablene i style.css.
"use strict";

(function () {
  const data = document.getElementById("grafdata");
  const lerret = document.getElementById("graf");
  if (!data || !lerret || typeof Chart === "undefined") {
    return; // Uten graf står tallene fortsatt i tabellen.
  }

  const graf = JSON.parse(data.textContent);
  const stil = getComputedStyle(document.documentElement);
  const farge = (navn) => stil.getPropertyValue(navn).trim();
  const linje = farge("--graf-linje");
  const bakgrunn = farge("--graf-bakgrunn");
  const tekst = farge("--graf-tekst");
  const rutenett = farge("--graf-rutenett");

  const prosent = (verdi) =>
    verdi.toLocaleString("nb-NO", {
      minimumFractionDigits: 1,
      maximumFractionDigits: 1,
    }) + " %";

  new Chart(lerret, {
    type: "line",
    data: {
      labels: graf.uker,
      datasets: [
        {
          label: graf.tekster.y,
          data: graf.andel,
          borderColor: linje,
          borderWidth: 2,
          spanGaps: false,
          pointStyle: "circle",
          pointRadius: 5,
          pointHoverRadius: 7,
          pointBorderWidth: 2,
          pointBorderColor: linje,
          // Usikre uker: åpen sirkel (hvit fyll), ikke bare en annen farge (NFR-7).
          pointBackgroundColor: graf.usikker.map((u) => (u ? bakgrunn : linje)),
        },
      ],
    },
    options: {
      maintainAspectRatio: false,
      animation: false,
      color: tekst,
      plugins: {
        legend: { display: false },
        tooltip: {
          callbacks: {
            label: (punkt) => prosent(punkt.parsed.y),
          },
        },
      },
      scales: {
        x: {
          title: { display: true, text: graf.tekster.x, color: tekst },
          ticks: { color: tekst },
          grid: { color: rutenett },
        },
        y: {
          beginAtZero: true,
          title: { display: true, text: graf.tekster.y, color: tekst },
          ticks: { color: tekst, callback: (verdi) => verdi + " %" },
          grid: { color: rutenett },
        },
      },
    },
  });
})();
