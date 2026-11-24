// All egen JavaScript for siden (AD-8).
//
// 1. Åpner en begrepsforklaring når en lenke peker på den, for eksempel
//    «Hva betyr dette?» i varselet (FR-19). Uten JavaScript fører lenken
//    fortsatt til forklaringen, som da åpnes med mus, Enter eller mellomrom.
// 2. Tegner grafen fra JSON-blokken `#grafdata`, som lages fra samme Dataserie
//    som tabellen. Tekstene står i malen (data-attributter og ferdig formaterte
//    andeler), og fargene kommer fra CSS-variablene i style.css. Uten
//    JavaScript eller Chart.js vises alternativteksten i stedet, og tallene står
//    i tabellen.
"use strict";

(function () {
  // Åpner forklaringen med id-en `id` (#begrep-…) og flytter fokus dit.
  function åpneBegrep(id) {
    const forklaring = id.startsWith("begrep-") && document.getElementById(id);
    if (forklaring && forklaring.tagName === "DETAILS") {
      forklaring.open = true;
      forklaring.querySelector("summary").focus();
    }
  }
  // Klikk på lenken. Gjelder også når adressen alt peker dit og
  // forklaringen er lukket igjen, for da kommer ingen «hashchange».
  document.addEventListener("click", (hendelse) => {
    const lenke = hendelse.target.closest('a[href^="#begrep-"]');
    if (lenke) {
      åpneBegrep(lenke.getAttribute("href").slice(1));
    }
  });
  // Adressen peker på en forklaring når siden lastes eller endres.
  const fraAdressen = () => åpneBegrep(decodeURIComponent(location.hash.slice(1)));
  window.addEventListener("hashchange", fraAdressen);
  fraAdressen();
})();

(function () {
  const data = document.getElementById("grafdata");
  const lerret = document.getElementById("graf");
  if (!data || !lerret || typeof Chart === "undefined") {
    return;
  }

  const graf = JSON.parse(data.textContent);
  const tekster = lerret.dataset;
  const stil = getComputedStyle(document.documentElement);
  const farge = (navn) => stil.getPropertyValue(navn).trim();
  const linje = farge("--graf-linje");
  const bakgrunn = farge("--graf-bakgrunn");
  const tekst = farge("--graf-tekst");
  const rutenett = farge("--graf-rutenett");

  // Vis grafen og skjul reserveteksten først når Chart.js er lastet.
  lerret.parentElement.hidden = false;
  const reserve = document.querySelector(".grafreserve");
  if (reserve) {
    reserve.hidden = true;
  }

  // Grafen bruker samme skrift som teksten og tegnes når skriften er lastet.
  Chart.defaults.font.family = farge("--skrift-tekst");
  const tegn = () =>
    new Chart(lerret, {
      type: "line",
      data: {
        labels: graf.uker,
        datasets: [
          {
            label: tekster.tekstY,
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
              // Samme tekst som i tabellen, og om uka er usikker.
              label: (punkt) => {
                const i = punkt.dataIndex;
                const usikker = graf.usikker[i] ? ", " + tekster.tekstUsikker : "";
                return graf.andel_tekst[i] + usikker;
              },
            },
          },
        },
        scales: {
          x: {
            title: { display: true, text: tekster.tekstX, color: tekst },
            ticks: { color: tekst },
            grid: { color: rutenett },
          },
          y: {
            beginAtZero: true,
            title: { display: true, text: tekster.tekstY, color: tekst },
            ticks: {
              color: tekst,
              callback: (verdi) => verdi.toLocaleString("nb-NO") + " %",
            },
            grid: { color: rutenett },
          },
        },
      },
    });
  (document.fonts ? document.fonts.ready : Promise.resolve()).then(tegn);
})();
