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
// 3. Henter KI-forklaringen fra `GET /forklaring` etter at siden er vist, og
//    setter fragmentet inn i forklaringsområdet (FR-20, AD-9). Området har
//    `aria-live="polite"`, så skjermlesere leser forklaringen når den kommer.
//    Ved nettverksfeil eller annen status enn 200 settes teksten fra
//    `data-feiltekst` inn (FR-22). Tekstene står i malene, ikke her.
"use strict";

(function () {
  const omraade = document.getElementById("forklaring");
  if (!omraade || !omraade.dataset.adresse) {
    return;
  }
  const visFeil = () => {
    const avsnitt = document.createElement("p");
    avsnitt.textContent = omraade.dataset.feiltekst;
    omraade.replaceChildren(avsnitt);
  };
  fetch(omraade.dataset.adresse, { headers: { Accept: "text/html" } })
    .then((svar) => {
      if (svar.status !== 200) {
        throw new Error("status " + svar.status);
      }
      return svar.text();
    })
    .then((html) => {
      // Fragmentet kommer fra vår egen server, og teksten fra Claude er
      // escapet av Jinja2.
      omraade.innerHTML = html;
    })
    .catch(visFeil);
})();

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

  // Punktene blir mindre jo smalere grafen er, så de ikke overlapper på
  // smale skjermer: radius er en tredel av plassen per uke, mellom 2 og 5
  // piksler (Irenes beslutning 24.11.2026).
  const radius = (ctx) => {
    const omraade = ctx.chart.chartArea;
    const bredde = omraade ? omraade.width : ctx.chart.width;
    const plass = bredde / Math.max(graf.uker.length, 1);
    return Math.min(5, Math.max(2, plass / 3));
  };

  // Radene i tabellen, i samme rekkefølge som ukene i grafen.
  const rader = [...document.querySelectorAll("tbody tr[data-indeks]")];

  // Markerer raden for uke nummer `indeks` i tabellen, eller ingen rad.
  // Markeringen er fet skrift og strek (style.css), ikke bare farge.
  function markerRad(indeks) {
    rader.forEach((rad) => {
      rad.classList.toggle("markert", Number(rad.dataset.indeks) === indeks);
    });
  }

  // Grafen bruker samme skrift som teksten og tegnes når skriften er lastet.
  Chart.defaults.font.family = farge("--skrift-tekst");
  const tegn = () => {
    const diagram = new Chart(lerret, {
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
            pointRadius: radius,
            pointHoverRadius: (ctx) => radius(ctx) + 3,
            pointBorderWidth: (ctx) => (radius(ctx) < 3 ? 1.5 : 2),
            pointHoverBorderWidth: 3,
            pointBorderColor: linje,
            // Usikre uker: åpen sirkel (hvit fyll), ikke bare en annen farge (NFR-7).
            pointBackgroundColor: graf.usikker.map((u) => (u ? bakgrunn : linje)),
          },
        ],
      },
      // Peker brukeren på en uke i grafen, markeres samme rad i tabellen.
      // Kjøres etter hver hendelse i grafen, også når musa forlater den, så
      // markeringen forsvinner igjen (`onHover` kalles ikke utenfor grafen).
      plugins: [
        {
          id: "markerRad",
          afterEvent: (diagrammet) => {
            const aktive = diagrammet.getActiveElements();
            markerRad(aktive.length ? aktive[0].index : null);
          },
        },
      ],
      options: {
        maintainAspectRatio: false,
        animation: false,
        color: tekst,
        // Uka nærmest musa langs den vannrette aksen, så små punkter er lette
        // å treffe.
        interaction: { mode: "index", intersect: false },
        plugins: {
          legend: { display: false },
          tooltip: {
            // Ingen fargerute: den sto bare ved første linje.
            displayColors: false,
            callbacks: {
              // Samme tall som i tabellen, og om uka er usikker.
              label: (punkt) => {
                const i = punkt.dataIndex;
                const linjer = [
                  tekster.tekstTester + ": " + graf.tester_tekst[i],
                  tekster.tekstPositive + ": " + graf.positive_tekst[i],
                  tekster.tekstAndel + ": " + graf.andel_tekst[i],
                ];
                if (graf.usikker[i]) {
                  linjer.push("(" + tekster.tekstUsikker + ")");
                }
                return linjer;
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
              callback: (verdi) => verdi.toLocaleString("nb-NO") + " %",
            },
            grid: { color: rutenett },
          },
        },
      },
    });

    // Markerer punktet for uke nummer `indeks` i grafen, med større punkt og
    // verktøytips, eller fjerner markeringen. Uker uten andel har ikke noe punkt.
    function markerPunkt(indeks) {
      const punkt =
        indeks === null || graf.andel[indeks] === null
          ? null
          : diagram.getDatasetMeta(0).data[indeks];
      const aktive = punkt ? [{ datasetIndex: 0, index: indeks }] : [];
      diagram.setActiveElements(aktive);
      const sted = punkt ? { x: punkt.x, y: punkt.y } : { x: 0, y: 0 };
      diagram.tooltip.setActiveElements(aktive, sted);
      diagram.update();
    }

    // Peker brukeren på eller går med tastaturet til en rad i tabellen,
    // markeres punktet i grafen og raden selv. Radene kan nås med Tab bare
    // når grafen finnes.
    rader.forEach((rad) => {
      const indeks = Number(rad.dataset.indeks);
      rad.tabIndex = 0;
      const vis = () => {
        markerRad(indeks);
        markerPunkt(indeks);
      };
      const skjul = () => {
        markerRad(null);
        markerPunkt(null);
      };
      rad.addEventListener("mouseenter", vis);
      rad.addEventListener("focus", vis);
      rad.addEventListener("mouseleave", skjul);
      rad.addEventListener("blur", skjul);
    });
  };
  (document.fonts ? document.fonts.ready : Promise.resolve()).then(tegn);
})();
