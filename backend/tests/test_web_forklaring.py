"""Tester for forklaringen på siden (story 4.5, FR-20, FR-22, NFR-2, AD-9).

Siden viser forklaringsområdet med «Forklaringen lages …», og `GET /forklaring`
gir fragmentet for de tre utfallene. FHI mockes med `respx`, cachen ligger i
`tmp_path`, og Claude er en falsk klient. Ingen test kaller Claude på ekte,
når nettet eller laster `.env` (AD-10).
"""

import html as htmllib
import json
import re
from collections.abc import Iterator
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Self

import anthropic
import httpx
import pytest
import respx
from anthropic.types import Message, TextBlock, Usage
from fastapi.testclient import TestClient
from markupsafe import escape

from backend import ki, tjeneste, web
from backend.config import Innstillinger
from backend.domene import Utvalg, kildehenvisning

FIXTURES = Path(__file__).parent / "fixtures"
DATA_URL = "https://statistikk-data.fhi.no/api/open/v1/msis/Table/724/data"
DIMENSJON_URL = "https://statistikk-data.fhi.no/api/open/v1/msis/Table/724/dimension"
NÅ = datetime(2026, 11, 24, 12, 0, tzinfo=UTC)
PARAMETRE = "mal=1&virus=influensa&sesong=2025%2F2026&alder=alle"
SIDE = "/resultat?" + PARAMETRE
FRAGMENT = "/forklaring?" + PARAMETRE
FORKLARING = (
    (FIXTURES / "ki" / "forklaring-influensa-2025-2026-alle.txt")
    .read_text(encoding="utf-8")
    .strip()
)
MANGLER_NØKKEL = (
    "KI-forklaringen krever en KI-nøkkel. Graf, tabell og varsel er komplette uten den."
)
KI_FEIL = "Forklaringen kunne ikke lages akkurat nå."


def _svar(navn: str) -> dict[str, Any]:
    return json.loads((FIXTURES / navn).read_text(encoding="utf-8"))["svar"]


DIMENSJONER = _svar("fhi/724-dimensjoner.json")
DATA = _svar("fhi/724-influensa-2025-2026-alle-nonstl.json")


def claude_svar(tekst: str = FORKLARING) -> Message:
    return Message(
        id="msg_falsk",
        type="message",
        role="assistant",
        model="claude-haiku-5-5",
        content=[TextBlock(type="text", text=tekst)],
        stop_reason="end_turn",
        stop_sequence=None,
        usage=Usage(input_tokens=1, output_tokens=1),
    )


class FalskClaude:
    """Står i stedet for `anthropic.Anthropic` og teller kallene."""

    def __init__(self, svaret: Any = None) -> None:
        self.svaret = claude_svar() if svaret is None else svaret
        self.kall = 0
        self.messages = self

    def __call__(self, **_: Any) -> Self:
        return self

    def __enter__(self) -> Self:
        return self

    def __exit__(self, *_: object) -> None:
        pass

    def create(self, **_: Any) -> Any:
        self.kall += 1
        if isinstance(self.svaret, BaseException):
            raise self.svaret
        return self.svaret


@pytest.fixture
def fhi_mock() -> Iterator[respx.MockRouter]:
    with respx.mock(assert_all_called=False) as router:
        router.get(DIMENSJON_URL, name="dimensjoner").respond(json=DIMENSJONER)
        router.post(DATA_URL, name="data").respond(json=DATA)
        yield router


def lag_klient(
    tmp_path: Path, claude: FalskClaude, nøkkel: str | None = "falsk-nøkkel"
) -> TestClient:
    innstillinger = Innstillinger(nøkkel, "claude-haiku-5-5", tmp_path / "cache")
    app = web.lag_app(lambda: innstillinger, klokke=lambda: NÅ, ny_ki_klient=claude)
    return TestClient(app)


@pytest.fixture
def claude() -> FalskClaude:
    return FalskClaude()


@pytest.fixture
def klient(
    tmp_path: Path, claude: FalskClaude, fhi_mock: respx.MockRouter
) -> Iterator[TestClient]:
    with lag_klient(tmp_path, claude) as testklient:
        yield testklient


@pytest.fixture
def uten_nøkkel(
    tmp_path: Path, claude: FalskClaude, fhi_mock: respx.MockRouter
) -> Iterator[TestClient]:
    with lag_klient(tmp_path, claude, nøkkel=None) as testklient:
        yield testklient


def _område(html: str) -> str:
    funn = re.search(r'<div id="forklaring"[^>]*>.*?</div>', html, re.DOTALL)
    assert funn, "fant ikke forklaringsområdet"
    return funn[0]


def _tekst(html: str) -> str:
    """Teksten i fragmentet uten tagger, med mellomrom samlet."""
    return " ".join(htmllib.unescape(re.sub(r"<[^>]+>", " ", html)).split())


# --- Området på siden (FR-20, AD-9) ---


def test_siden_har_området_med_aria_live_og_ventetekst(klient: TestClient) -> None:
    område = _område(klient.get(SIDE).text)
    assert 'aria-live="polite"' in område
    assert "<p>Forklaringen lages …</p>" in område


def test_området_peker_på_forklaringen_med_samme_parametre(
    klient: TestClient,
) -> None:
    område = _område(klient.get(SIDE).text)
    assert f'data-adresse="{escape(FRAGMENT)}"' in område


def test_feilteksten_står_i_malen(klient: TestClient) -> None:
    område = _område(klient.get(SIDE).text)
    assert f'data-feiltekst="{KI_FEIL}"' in område


def test_områdets_overskrift_og_plass_etter_begrepene(klient: TestClient) -> None:
    html = klient.get(SIDE).text
    assert '<h2 id="forklaringstittel">Forklaring</h2>' in html
    # Boks 6 i skissen i PRD §6.0: etter begrepene. «Hvorfor ikke …» står på
    # forsiden fra 25.11.2026 (FR-27), så området er siste del av siden.
    assert html.index('id="begrepstittel"') < html.index('id="forklaring"')
    assert 'id="chatbottittel"' not in html


def test_uten_javascript_sier_siden_det(klient: TestClient) -> None:
    html = klient.get(SIDE).text
    assert re.search(
        r"<noscript><p>KI-forklaringen krever JavaScript\. Graf, tabell og varsel "
        r"er komplette uten den\.</p></noscript>",
        html,
    )


def test_siden_kaller_ikke_claude(klient: TestClient, claude: FalskClaude) -> None:
    # Siden venter ikke på KI-en (NFR-2, AD-9).
    assert klient.get(SIDE).status_code == 200
    assert claude.kall == 0


def test_siden_kaller_ikke_ki(
    klient: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    def stopp(*_: Any, **__: Any) -> None:
        raise AssertionError("GET / skal ikke kalle ki")

    monkeypatch.setattr(ki, "forklar", stopp)
    monkeypatch.setattr(ki, "nøkkel", stopp)
    monkeypatch.setattr(tjeneste.Tjeneste, "forklaring", stopp)
    assert klient.get(SIDE).status_code == 200


@pytest.mark.parametrize(
    "sti",
    [
        "/resultat?mal=1&virus=ebola&sesong=2025/2026&alder=alle",
        "/resultat?mal=1&virus=influensa&sesong=1999/2000",
    ],
)
def test_uten_tall_vises_ikke_området(klient: TestClient, sti: str) -> None:
    html = klient.get(sti).text
    assert 'id="forklaring"' not in html
    assert "Forklaringen lages" not in html


def test_uten_tall_fra_fhi_vises_ikke_området(
    klient: TestClient, fhi_mock: respx.MockRouter
) -> None:
    # Gyldig utvalg, men FHI svarer ikke og ingen tall er lagret.
    fhi_mock.routes["data"].respond(status_code=503)
    html = klient.get(SIDE).text
    assert 'role="status"' in html
    assert 'id="forklaring"' not in html
    assert "Forklaringen lages" not in html


def test_med_lagrede_tall_vises_siden_uten_fhi_og_uten_ki(
    klient: TestClient,
    claude: FalskClaude,
    fhi_mock: respx.MockRouter,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # NFR-2: med lagrede tall vises graf, tabell og varsel uten å vente på
    # FHI eller KI-en.
    assert klient.get(SIDE).status_code == 200
    kall_til_fhi = fhi_mock.routes["data"].call_count

    def stopp(*_: Any, **__: Any) -> None:
        raise AssertionError("GET / skal ikke kalle ki")

    monkeypatch.setattr(tjeneste.Tjeneste, "forklaring", stopp)
    html = klient.get(SIDE).text
    assert fhi_mock.routes["data"].call_count == kall_til_fhi
    assert 'id="graf"' in html
    assert "<tbody>" in html
    assert "Forklaringen lages …" in html
    assert claude.kall == 0


def test_app_js_henter_fragmentet_og_bruker_feilteksten() -> None:
    kode = (Path(web.__file__).parent / "static" / "app.js").read_text("utf-8")
    assert 'getElementById("forklaring")' in kode
    assert "fetch(omraade.dataset.adresse" in kode
    assert "svar.status !== 200" in kode
    assert "omraade.dataset.feiltekst" in kode
    # Tekstene står i malene, ikke i JavaScript (AD-9).
    assert KI_FEIL not in kode
    assert "KI-nøkkel" not in kode


# --- Fragmentet: forklaringen (FR-20, FR-12) ---


def test_fragmentet_har_forklaringen_merket_skrevet_av_ki(
    klient: TestClient, claude: FalskClaude
) -> None:
    svar = klient.get(FRAGMENT)
    assert svar.status_code == 200
    assert svar.headers["content-type"].startswith("text/html")
    assert '<p class="ki-merke">Skrevet av KI</p>' in svar.text
    assert _tekst(svar.text).startswith("Skrevet av KI " + " ".join(FORKLARING.split()))
    assert claude.kall == 1


def test_fragmentet_har_kildehenvisningen(klient: TestClient) -> None:
    svar = klient.get(FRAGMENT)
    kilde = web.kildetekst(kildehenvisning(724, NÅ))
    assert f'<p class="kilde">{escape(kilde)}</p>' in svar.text


def test_kildehenvisningen_er_den_samme_som_under_tabellen(
    klient: TestClient,
) -> None:
    side = klient.get(SIDE).text
    fragment = klient.get(FRAGMENT).text
    under_tabellen = re.search(r'<p class="kilde">.*?</p>', side)
    ved_forklaringen = re.search(r'<p class="kilde">.*?</p>', fragment)
    assert under_tabellen and ved_forklaringen
    assert under_tabellen[0] == ved_forklaringen[0]


def test_avsnitt_i_forklaringen_blir_egne_avsnitt(
    tmp_path: Path, fhi_mock: respx.MockRouter
) -> None:
    claude = FalskClaude(claude_svar("Første avsnitt.\n\n  \nAndre avsnitt.\n"))
    with lag_klient(tmp_path, claude) as testklient:
        svar = testklient.get(FRAGMENT).text
    assert "<p>Første avsnitt.</p>" in svar
    assert "<p>Andre avsnitt.</p>" in svar


def test_teksten_fra_claude_escapes(tmp_path: Path, fhi_mock: respx.MockRouter) -> None:
    claude = FalskClaude(claude_svar('<script>alert("x")</script> & mer'))
    with lag_klient(tmp_path, claude) as testklient:
        svar = testklient.get(FRAGMENT).text
    assert "<script>" not in svar
    assert "&lt;script&gt;" in svar
    assert "&amp; mer" in svar


def test_fragmentet_lagres_ikke_av_nettleseren(klient: TestClient) -> None:
    assert klient.get(FRAGMENT).headers["cache-control"] == "no-store"


# --- Fragmentet: uten nøkkel og ved feil (FR-22) ---


def test_uten_nøkkel_sier_fragmentet_at_nøkkel_trengs(
    uten_nøkkel: TestClient, claude: FalskClaude
) -> None:
    svar = uten_nøkkel.get(FRAGMENT)
    assert svar.status_code == 200
    assert _tekst(svar.text) == MANGLER_NØKKEL
    assert "Skrevet av KI" not in svar.text
    assert claude.kall == 0


def test_uten_nøkkel_brukes_ikke_en_lagret_forklaring(
    tmp_path: Path, claude: FalskClaude, fhi_mock: respx.MockRouter
) -> None:
    # Irenes beslutning på PR #67: uten nøkkel står det at nøkkel trengs,
    # også når en forklaring er lagret (FR-22).
    with lag_klient(tmp_path, claude) as testklient:
        assert "Skrevet av KI" in testklient.get(FRAGMENT).text
    with lag_klient(tmp_path, claude, nøkkel=None) as testklient:
        assert _tekst(testklient.get(FRAGMENT).text) == MANGLER_NØKKEL


@pytest.mark.parametrize(
    "svaret",
    [
        anthropic.APIConnectionError(request=httpx.Request("POST", "https://x")),
        RuntimeError("uventet"),
        claude_svar(""),
    ],
    ids=["nettverksfeil", "uventet-feil", "tomt-svar"],
)
def test_ved_kifeil_gir_fragmentet_feilteksten(
    tmp_path: Path, fhi_mock: respx.MockRouter, svaret: Any
) -> None:
    claude = FalskClaude(svaret)
    with lag_klient(tmp_path, claude) as testklient:
        svar = testklient.get(FRAGMENT)
    assert svar.status_code == 200
    assert _tekst(svar.text) == KI_FEIL
    assert "Skrevet av KI" not in svar.text


def test_feilteksten_er_den_samme_i_fragmentet_og_på_siden(
    tmp_path: Path, fhi_mock: respx.MockRouter
) -> None:
    claude = FalskClaude(RuntimeError("uventet"))
    with lag_klient(tmp_path, claude) as testklient:
        side = testklient.get(SIDE).text
        fragment = testklient.get(FRAGMENT).text
    feiltekst = re.search(r'data-feiltekst="([^"]*)"', side)
    assert feiltekst
    assert htmllib.unescape(feiltekst[1]) == _tekst(fragment)


def test_uten_tall_gir_fragmentet_feilteksten(
    klient: TestClient, claude: FalskClaude, fhi_mock: respx.MockRouter
) -> None:
    fhi_mock.routes["data"].respond(status_code=503)
    svar = klient.get(FRAGMENT)
    assert svar.status_code == 200
    assert _tekst(svar.text) == KI_FEIL
    assert claude.kall == 0


@pytest.mark.parametrize(
    "parametre",
    [
        "",
        "mal=1&virus=influensa&sesong=1999%2F2000&alder=alle",
        "mal=9",
        "mal=1&virus=ebola&sesong=2025%2F2026&alder=alle",
    ],
)
def test_ugyldig_utvalg_gir_400(
    klient: TestClient, claude: FalskClaude, parametre: str
) -> None:
    svar = klient.get("/forklaring?" + parametre)
    assert svar.status_code == 400
    assert claude.kall == 0


def test_forklaringsadresse_lager_samme_parametre_som_skjemaet() -> None:
    adresse = web.forklaringsadresse(Utvalg(1, "influensa", "2025/2026", "80+"))
    assert adresse == "/forklaring?mal=1&virus=influensa&sesong=2025%2F2026&alder=80%2B"
