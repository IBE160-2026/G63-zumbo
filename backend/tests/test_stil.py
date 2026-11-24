"""Tester for stilen og de faste tekstene på siden (story 3.7).

Kontrasten regnes ut fra CSS-variablene i `style.css` etter WCAG 2.1 (NFR-4).
Andre tester sjekker fokusmarkering (NFR-5), mobil (NFR-11), at alle skjemafelt
har `<label>`, skriftene og tekstene Irene valgte 24.11.2026, og FR-26.
"""

import json
import re
from collections.abc import Iterator
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import pytest
import respx
from fastapi.testclient import TestClient

from backend import mellomlager, web
from backend.config import Innstillinger
from backend.domene import Utvalg

FIXTURES = Path(__file__).parent / "fixtures"
DATA_URL = "https://statistikk-data.fhi.no/api/open/v1/msis/Table/724/data"
DIMENSJON_URL = "https://statistikk-data.fhi.no/api/open/v1/msis/Table/724/dimension"
STATIC = Path(web.__file__).parent / "static"
TEMPLATES = Path(web.__file__).parent / "templates"
CSS = (STATIC / "style.css").read_text(encoding="utf-8")
APP_JS = (STATIC / "app.js").read_text(encoding="utf-8")
NÅ = datetime(2026, 11, 24, 12, 0, tzinfo=UTC)
HENTET = datetime(2026, 11, 24, 10, 5, tzinfo=UTC)
UTVALG = Utvalg(1, "influensa", "2025/2026", "alle")
STI = "/?mal=1&virus=influensa&sesong=2025/2026&alder=alle"
DATA = "fhi/724-influensa-2025-2026-alle-nonstl.json"

AVSENDER = (
    "Laget av en student ved Høgskolen i Molde, med tall fra FHI. "
    "Dette er ikke en tjeneste fra FHI."
)
JUSTERING = "Tallene for den siste uka kan bli justert når flere prøvesvar kommer inn."
CHATBOT_TITTEL = "Hvorfor ikke bare spørre en chatbot?"
CHATBOT_TEKST = (
    "En chatbot kan finne på tall eller bruke gamle tall, og den sier sjelden "
    "hvor tallene kommer fra. Denne appen henter tallene direkte fra "
    "Folkehelseinstituttet, viser når de ble hentet, og sier fra når det er for "
    "lite data til å konkludere. KI brukes bare til å forklare tallene med enkle "
    "ord, aldri til å lage dem."
)


def _svar(navn: str) -> dict[str, Any]:
    return json.loads((FIXTURES / navn).read_text(encoding="utf-8"))["svar"]


# --- Fargene og kontrasten (NFR-4) ---


def _rot() -> str:
    treff = re.search(r":root\s*\{(.*?)\}", CSS, re.DOTALL)
    assert treff, "style.css mangler :root"
    return treff[1]


def variabler() -> dict[str, str]:
    """Alle CSS-variabler i :root, med `var(--x)` slått opp."""
    rå = dict(re.findall(r"(--[a-z-]+)\s*:\s*([^;]+);", _rot()))
    verdier: dict[str, str] = {}
    for navn, verdi in rå.items():
        while m := re.fullmatch(r"var\((--[a-z-]+)\)", verdi.strip()):
            verdi = rå[m[1]]
        verdier[navn] = verdi.strip()
    return verdier


def luminans(farge: str) -> float:
    """Relativ luminans etter WCAG 2.1."""
    assert re.fullmatch(r"#[0-9A-Fa-f]{6}", farge), farge
    kanaler = [int(farge[i : i + 2], 16) / 255 for i in (1, 3, 5)]
    r, g, b = (
        k / 12.92 if k <= 0.04045 else ((k + 0.055) / 1.055) ** 2.4 for k in kanaler
    )
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def kontrast(a: str, b: str) -> float:
    lys, mørk = sorted((luminans(a), luminans(b)), reverse=True)
    return (lys + 0.05) / (mørk + 0.05)


def test_kontrastberegningen() -> None:
    assert kontrast("#000000", "#FFFFFF") == pytest.approx(21)
    assert kontrast("#FFFFFF", "#FFFFFF") == pytest.approx(1)
    # Kjent verdi: #767676 er den lyseste grå med 4,5:1 mot hvitt.
    assert kontrast("#767676", "#FFFFFF") == pytest.approx(4.54, abs=0.01)


def test_fargene_er_fhis_palett() -> None:
    v = variabler()
    assert v["--hovedfarge"].upper() == "#386E84"
    assert v["--varselfarge"].upper() == "#D14641"
    assert v["--bakgrunn"].upper() == "#FFFFFF"
    assert v["--tekst"].upper() == "#222222"


@pytest.mark.parametrize(
    ("forgrunn", "bakgrunn", "grense"),
    [
        ("--tekst", "--bakgrunn", 4.5),  # vanlig tekst
        ("--hovedfarge", "--bakgrunn", 4.5),  # lenker og fokusmarkering
        ("--knappetekst", "--hovedfarge", 4.5),  # tekst på knappen
        ("--varselfarge", "--bakgrunn", 4.5),  # ikonet og rammen i varselet
        ("--graf-tekst", "--graf-bakgrunn", 4.5),  # akser og etiketter i grafen
        ("--graf-linje", "--graf-bakgrunn", 3.0),  # linje og punkter i grafen
    ],
)
def test_kontrasten_holder_grensene(
    forgrunn: str, bakgrunn: str, grense: float
) -> None:
    v = variabler()
    assert kontrast(v[forgrunn], v[bakgrunn]) >= grense


def test_farger_står_bare_som_variabler_i_root() -> None:
    """Alle farger i stilen kommer fra variablene, så testene over dekker dem."""
    utenfor = CSS.replace(_rot(), "")
    assert not re.findall(r"#[0-9A-Fa-f]{3,8}\b|rgba?\(|hsla?\(", utenfor)


def test_app_js_leser_graffargene_og_skriften_fra_variablene() -> None:
    lest = re.findall(r'farge\("(--[a-z-]+)"\)', APP_JS)
    assert {"--graf-linje", "--graf-bakgrunn", "--graf-tekst"} <= set(lest)
    v = variabler()
    for navn in lest:
        assert navn in v, navn


# --- Fokusmarkering (NFR-5) og mobil (NFR-11) ---


def test_synlig_fokusmarkering_på_alt_som_kan_nås_med_tab() -> None:
    uten_kommentarer = re.sub(r"/\*.*?\*/", "", CSS, flags=re.DOTALL)
    regel = re.search(r"([^{}]*:focus-visible[^{}]*)\{([^}]*)\}", uten_kommentarer)
    assert regel
    velgere = {v.strip() for v in regel[1].split(",")}
    for element in ("a", "button", "select", "summary", "[tabindex]"):
        assert f"{element}:focus-visible" in velgere
    assert re.search(r"outline:\s*3px solid var\(--hovedfarge\)", regel[2])
    assert "outline: none" not in CSS
    assert "outline: 0" not in CSS


def _blokk(velger: str) -> str:
    treff = re.search(rf"(?m)^{re.escape(velger)}\s*\{{([^}}]*)\}}", CSS)
    assert treff, velger
    return treff[1]


def test_smal_skjerm_uten_vannrett_rulling() -> None:
    assert "overflow-x: auto" in _blokk(".tabellboks")
    assert "max-width: 100%" in CSS.split("select,\nbutton {")[1].split("}")[0]
    assert "box-sizing: border-box" in CSS


# --- Skriftene ---


def test_skriftene_ligger_lokalt_med_lisens() -> None:
    filer = re.findall(r'url\("fonts/([^"]+)"\)', CSS)
    assert sorted(filer) == ["fraunces.woff2", "poppins-400.woff2", "poppins-600.woff2"]
    for fil in filer:
        assert (STATIC / "fonts" / fil).read_bytes()[:4] == b"wOF2"
    for lisens in ("OFL-fraunces.txt", "OFL-poppins.txt"):
        tekst = (STATIC / "fonts" / lisens).read_text(encoding="utf-8")
        assert "SIL Open Font License, Version 1.1" in tekst
    alt = CSS + "".join(p.read_text(encoding="utf-8") for p in TEMPLATES.iterdir())
    assert "googleapis" not in alt
    assert "gstatic" not in alt


def test_overskrifter_i_fraunces_og_tekst_i_poppins() -> None:
    overskrift = _blokk("h1,\nh2")
    assert "var(--skrift-overskrift)" in overskrift
    assert 'font-variation-settings: "SOFT" 100, "WONK" 0' in overskrift
    assert "font-weight: 700" in overskrift
    assert "var(--skrift-tekst)" in _blokk("body")
    v = variabler()
    assert v["--skrift-overskrift"].startswith('"Fraunces"')
    assert v["--skrift-tekst"].startswith('"Poppins"')


# --- Siden ---


@pytest.fixture
def klient(tmp_path: Path) -> Iterator[TestClient]:
    mappe = tmp_path / "cache"
    mellomlager.lagre_svar(mappe, UTVALG, _svar(DATA), HENTET)
    with respx.mock(assert_all_called=False) as router:
        router.get(DIMENSJON_URL).respond(json=_svar("fhi/724-dimensjoner.json"))
        router.post(DATA_URL).respond(json=_svar(DATA))
        innstillinger = Innstillinger(None, "modell", mappe)
        app = web.lag_app(lambda: innstillinger, klokke=lambda: NÅ)
        with TestClient(app) as testklient:
            yield testklient


@pytest.mark.parametrize("sti", ["/", STI, "/?alder=ukjent"])
def test_alle_skjemafelt_har_label(klient: TestClient, sti: str) -> None:
    html = klient.get(sti).text
    felt = re.findall(r"<(?:select|input|textarea)\b[^>]*\bid=\"([^\"]+)\"", html)
    alle_felt = re.findall(r"<(?:select|input|textarea)\b", html)
    assert len(felt) == len(alle_felt) == 4
    etiketter = re.findall(r'<label for="([^"]+)">[^<]+</label>', html)
    assert sorted(felt) == sorted(etiketter)


def test_skriftfilene_serveres(klient: TestClient) -> None:
    svar = klient.get("/static/fonts/fraunces.woff2")
    assert svar.status_code == 200
    assert svar.content[:4] == b"wOF2"


def _tekst(html: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", html))


def test_avsenderlinjen_og_ingen_logo(klient: TestClient) -> None:
    for sti in ("/", STI):
        html = klient.get(sti).text
        bunn = re.search(r'<footer class="avsender">(.*?)</footer>', html, re.DOTALL)
        assert bunn and _tekst(bunn[1]).strip() == AVSENDER
        assert "<img" not in html


def test_justering_står_rett_under_hentetidspunktet(klient: TestClient) -> None:
    html = klient.get(STI).text
    kilde = html.index('<p class="kilde">')
    justering = html.index(f'<p class="justering">{JUSTERING}</p>')
    assert "Hentet 24.11.2026 kl. 11:05." in html[kilde:justering]
    assert html[kilde:justering].count("<p") == 1


def test_justering_vises_ikke_uten_tall(klient: TestClient) -> None:
    assert JUSTERING not in klient.get("/").text


def test_varselets_overskrift_er_uendret() -> None:
    mal = (TEMPLATES / "index.html").read_text(encoding="utf-8")
    assert "</span> For tynt datagrunnlag</h2>" in mal


@pytest.mark.parametrize("sti", ["/", STI])
def test_chatbotteksten_står_nederst_på_siden(klient: TestClient, sti: str) -> None:
    """FR-26 (Irenes beslutning 24.11.2026)."""
    html = klient.get(sti).text
    del_ = re.search(r'<section class="om-appen"(.*?)</section>', html, re.DOTALL)
    assert del_
    assert f'<h2 id="chatbottittel">{CHATBOT_TITTEL}</h2>' in del_[1]
    assert f"<p>{CHATBOT_TEKST}</p>" in del_[1]
    # Siste del av innholdet, under begrepsforklaringene og over avsenderlinjen.
    assert html.index('<section class="begreper"') < html.index(
        '<section class="om-appen"'
    )
    etter = html[html.index('<section class="om-appen"') :]
    assert "<section" not in etter[1:]
    assert etter.index("</main>") < etter.index('<footer class="avsender">')
