"""Tester for «Hent nyeste tall nå» (story 4.6, FR-25, FR-8, AD-7, AD-9).

FHI mockes med `respx`, cachen ligger i `tmp_path`, klokka styres av testen,
og Claude er en falsk klient. Ingen test kaller FHI eller Claude på ekte, eller
laster `.env` (AD-10).
"""

import json
import re
from collections.abc import Iterator
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any, Self
from urllib.parse import parse_qs, urlsplit

import httpx
import pytest
import respx
from anthropic.types import Message, TextBlock, Usage
from fastapi.testclient import TestClient

from backend import mellomlager, web
from backend.config import Innstillinger
from backend.domene import Utvalg

FIXTURES = Path(__file__).parent / "fixtures"
DATA_URL = "https://statistikk-data.fhi.no/api/open/v1/msis/Table/724/data"
DIMENSJON_URL = "https://statistikk-data.fhi.no/api/open/v1/msis/Table/724/dimension"
UTVALG = Utvalg(1, "influensa", "2025/2026", "alle")
SKJEMA = {"mal": "1", "virus": "influensa", "sesong": "2025/2026", "alder": "alle"}
SIDE = "/?mal=1&virus=influensa&sesong=2025%2F2026&alder=alle"
FRAGMENT = "/forklaring?mal=1&virus=influensa&sesong=2025%2F2026&alder=alle"
START = datetime(2026, 11, 24, 12, 0, tzinfo=UTC)
FORKLARING = (
    (FIXTURES / "ki" / "forklaring-influensa-2025-2026-alle.txt")
    .read_text(encoding="utf-8")
    .strip()
)


def _svar(navn: str) -> dict[str, Any]:
    return json.loads((FIXTURES / navn).read_text(encoding="utf-8"))["svar"]


DIMENSJONER = _svar("fhi/724-dimensjoner.json")
DATA = _svar("fhi/724-influensa-2025-2026-alle-nonstl.json")
R1_19 = _svar("konstruert/724-r1-19-positive.json")


class Klokke:
    """En klokke testen kan stille fram."""

    def __init__(self) -> None:
        self.nå = START

    def __call__(self) -> datetime:
        return self.nå


class FalskClaude:
    """Står i stedet for `anthropic.Anthropic` og teller kallene."""

    def __init__(self) -> None:
        self.kall = 0
        self.messages = self

    def __call__(self, **_: Any) -> Self:
        return self

    def __enter__(self) -> Self:
        return self

    def __exit__(self, *_: object) -> None:
        pass

    def create(self, **_: Any) -> Message:
        self.kall += 1
        return Message(
            id="msg_falsk",
            type="message",
            role="assistant",
            model="claude-haiku-5-5",
            content=[TextBlock(type="text", text=FORKLARING)],
            stop_reason="end_turn",
            stop_sequence=None,
            usage=Usage(input_tokens=1, output_tokens=1),
        )


@pytest.fixture
def fhi_mock() -> Iterator[respx.MockRouter]:
    with respx.mock(assert_all_called=False) as router:
        router.get(DIMENSJON_URL, name="dimensjoner").respond(json=DIMENSJONER)
        router.post(DATA_URL, name="data").respond(json=DATA)
        yield router


@pytest.fixture
def mappe(tmp_path: Path) -> Path:
    return tmp_path / "cache"


@pytest.fixture
def klokke() -> Klokke:
    return Klokke()


@pytest.fixture
def claude() -> FalskClaude:
    return FalskClaude()


@pytest.fixture
def klient(
    mappe: Path, klokke: Klokke, claude: FalskClaude, fhi_mock: respx.MockRouter
) -> Iterator[TestClient]:
    innstillinger = Innstillinger("falsk-nøkkel", "claude-haiku-5-5", mappe)
    app = web.lag_app(lambda: innstillinger, klokke=klokke, ny_ki_klient=claude)
    with TestClient(app, follow_redirects=False) as testklient:
        yield testklient


def _fhi_nede(router: respx.MockRouter) -> None:
    feil = httpx.ConnectError("nede")
    router.routes["dimensjoner"].mock(side_effect=feil)
    router.routes["data"].mock(side_effect=feil)


def _parametre(adresse: str) -> dict[str, list[str]]:
    del_ = urlsplit(adresse)
    assert del_.path == "/"
    return parse_qs(del_.query)


# --- Siden: hentetidspunkt, torsdag og knappen (FR-25, NFR-5) ---


def test_siden_sier_når_tallene_ble_hentet_og_at_fhi_publiserer_på_torsdag(
    klient: TestClient,
) -> None:
    html = klient.get(SIDE).text
    assert "Hentet 24.11.2026 kl. 13:00." in html
    assert '<p class="publisering">FHI publiserer nye tall hver torsdag.</p>' in html


def test_knappen_sender_post_med_samme_utvalg(klient: TestClient) -> None:
    html = klient.get(SIDE).text
    skjema = re.search(
        r'<form method="post" action="/hent-nyeste" class="hent-nyeste">(.*?)</form>',
        html,
        re.DOTALL,
    )
    assert skjema, "fant ikke skjemaet for knappen"
    felt = dict(
        re.findall(r'<input type="hidden" name="(\w+)" value="([^"]*)">', skjema[1])
    )
    assert felt == SKJEMA
    # En vanlig knapp, så den kan brukes med Tab, Enter og mellomrom (NFR-5).
    assert re.search(r'<button type="submit"[^>]*>Hent nyeste tall nå</button>', html)


@pytest.mark.parametrize("sti", ["/", "/?mal=1&virus=influensa&sesong=1999/2000"])
def test_uten_tall_vises_ikke_knappen(klient: TestClient, sti: str) -> None:
    assert "Hent nyeste tall nå" not in klient.get(sti).text


def test_app_js_deaktiverer_knappen_når_skjemaet_sendes() -> None:
    kode = (Path(web.__file__).parent / "static" / "app.js").read_text("utf-8")
    assert 'querySelectorAll("form.hent-nyeste")' in kode
    assert 'addEventListener("submit"' in kode
    assert "knapp.disabled = true" in kode
    assert "knapp.dataset.ventetekst" in kode
    assert 'addEventListener("pageshow"' in kode
    # Tekstene står i malen.
    assert "Henter nyeste tall" not in kode


# --- POST /hent-nyeste (FR-25, AD-9) ---


def test_post_svarer_303_til_samme_utvalg(klient: TestClient) -> None:
    svar = klient.post("/hent-nyeste", data=SKJEMA)
    assert svar.status_code == 303
    assert _parametre(svar.headers["location"]) == {
        navn: [verdi] for navn, verdi in SKJEMA.items()
    }


def test_post_henter_uten_mellomlager_og_lagrer_med_nytt_hentetidspunkt(
    klient: TestClient, mappe: Path, klokke: Klokke, fhi_mock: respx.MockRouter
) -> None:
    mellomlager.lagre_svar(mappe, UTVALG, R1_19, START - timedelta(hours=1))
    klient.get(SIDE)
    assert fhi_mock.routes["data"].call_count == 0  # de lagrede tallene er ferske

    klokke.nå = START + timedelta(minutes=10)
    klient.post("/hent-nyeste", data=SKJEMA)
    assert fhi_mock.routes["data"].call_count == 1
    lagret = mellomlager.les_svar(mappe, UTVALG)
    assert lagret is not None and lagret.svar == DATA and lagret.hentet == klokke.nå

    html = klient.get(SIDE).text
    assert "Hentet 24.11.2026 kl. 13:10." in html
    assert fhi_mock.routes["data"].call_count == 1


def test_post_og_omdirigering_gir_siden_med_de_nye_tallene(
    klient: TestClient,
) -> None:
    svar = klient.post("/hent-nyeste", data=SKJEMA, follow_redirects=True)
    assert svar.status_code == 200
    assert str(svar.url).endswith(SIDE)
    assert "<tbody>" in svar.text
    assert 'role="status"' not in svar.text


def test_fhi_nede_gir_sist_lagrede_tall_med_dato(
    klient: TestClient, mappe: Path, klokke: Klokke, fhi_mock: respx.MockRouter
) -> None:
    mellomlager.lagre_svar(mappe, UTVALG, DATA, START - timedelta(hours=1))
    _fhi_nede(fhi_mock)
    svar = klient.post("/hent-nyeste", data=SKJEMA)
    assert svar.status_code == 303
    assert _parametre(svar.headers["location"])[web.NYESTE] == [
        str(int(START.timestamp()))
    ]

    html = klient.get(svar.headers["location"]).text
    assert "Tallene kunne ikke hentes fra FHI akkurat nå." in html
    assert "Sist lagrede tall, hentet 24.11.2026 kl. 12:00." in html
    assert "<tbody>" in html
    # De lagrede tallene er urørt.
    lagret = mellomlager.les_svar(mappe, UTVALG)
    assert lagret is not None and lagret.hentet == START - timedelta(hours=1)


def test_fhi_nede_uten_lagrede_tall_gir_meldingen_uten_tall(
    klient: TestClient, fhi_mock: respx.MockRouter
) -> None:
    _fhi_nede(fhi_mock)
    svar = klient.post("/hent-nyeste", data=SKJEMA, follow_redirects=True)
    assert "det finnes ingen lagrede tall" in svar.text
    assert "<tbody>" not in svar.text


def _merket(tidspunkt: datetime) -> str:
    return f"{SIDE}&{web.NYESTE}={int(tidspunkt.timestamp())}"


def test_merket_endrer_ikke_en_side_uten_tall(
    klient: TestClient, fhi_mock: respx.MockRouter
) -> None:
    _fhi_nede(fhi_mock)
    html = klient.get(_merket(START)).text
    assert "det finnes ingen lagrede tall" in html
    assert "Sist lagrede tall" not in html


def test_merket_gjelder_ikke_når_adressen_lastes_inn_senere(
    klient: TestClient, mappe: Path, klokke: Klokke
) -> None:
    mellomlager.lagre_svar(mappe, UTVALG, DATA, START - timedelta(hours=1))
    klokke.nå = START + web.NYESTE_GJELDER + timedelta(seconds=1)
    html = klient.get(_merket(START)).text
    assert "Sist lagrede tall" not in html
    assert 'role="status"' not in html


def test_merket_gjelder_ikke_for_tall_hentet_etter_forsøket(
    klient: TestClient, mappe: Path, klokke: Klokke, fhi_mock: respx.MockRouter
) -> None:
    # De lagrede tallene er utdaterte, og FHI svarer igjen når siden vises.
    mellomlager.lagre_svar(mappe, UTVALG, DATA, START - timedelta(hours=30))
    klokke.nå = START + timedelta(minutes=2)
    html = klient.get(_merket(START)).text
    assert fhi_mock.routes["data"].call_count == 1
    assert "Sist lagrede tall" not in html
    assert "Hentet 24.11.2026 kl. 13:02." in html


@pytest.mark.parametrize("verdi", ["feilet", "", "-1", "99999999999999999999"])
def test_merket_med_ugyldig_verdi_ignoreres(
    klient: TestClient, mappe: Path, verdi: str
) -> None:
    mellomlager.lagre_svar(mappe, UTVALG, DATA, START - timedelta(hours=1))
    html = klient.get(f"{SIDE}&{web.NYESTE}={verdi}").text
    assert "Sist lagrede tall" not in html


def test_data_nede_etter_dimensjonslisten_venter_ikke_på_fhi_to_ganger(
    klient: TestClient, mappe: Path, fhi_mock: respx.MockRouter
) -> None:
    # Dimensjonslisten svarer, men tallene gjør det ikke, og de lagrede er
    # utdaterte. Siden etter omdirigeringen prøver ikke FHI igjen (FR-8).
    mellomlager.lagre_svar(mappe, UTVALG, DATA, START - timedelta(hours=30))
    fhi_mock.routes["data"].mock(side_effect=httpx.ConnectError("nede"))
    svar = klient.post("/hent-nyeste", data=SKJEMA, follow_redirects=True)
    assert fhi_mock.routes["data"].call_count == 1
    assert "Sist lagrede tall, hentet 23.11.2026 kl. 07:00." in svar.text


def test_gyldig_utvalg_uten_tall_har_knappen_og_teksten_om_torsdag(
    klient: TestClient, fhi_mock: respx.MockRouter
) -> None:
    # Brukeren kan prøve igjen, for eksempel når FHI har publisert på torsdag.
    _fhi_nede(fhi_mock)
    html = klient.get(SIDE).text
    assert "det finnes ingen lagrede tall" in html
    assert "FHI publiserer nye tall hver torsdag." in html
    assert "Hent nyeste tall nå" in html


def test_virus_som_ikke_er_klart_har_ikke_knappen(klient: TestClient) -> None:
    html = klient.get("/?mal=1&virus=rsv&sesong=2025%2F2026&alder=alle").text
    assert "Hent nyeste tall nå" not in html


@pytest.mark.parametrize(
    "skjema",
    [
        {},
        {**SKJEMA, "sesong": "1999/2000"},
        {**SKJEMA, "mal": "9"},
    ],
)
def test_ugyldig_utvalg_hentes_ikke_og_sendes_til_siden(
    klient: TestClient, fhi_mock: respx.MockRouter, skjema: dict[str, str]
) -> None:
    svar = klient.post("/hent-nyeste", data=skjema)
    assert svar.status_code == 303
    assert urlsplit(svar.headers["location"]).path == "/"
    assert web.NYESTE not in _parametre(svar.headers["location"])
    assert fhi_mock.routes["data"].call_count == 0


def test_ugyldig_utvalg_gir_feilmeldingen_på_siden(klient: TestClient) -> None:
    svar = klient.post(
        "/hent-nyeste",
        data={**SKJEMA, "sesong": "1999/2000"},
        follow_redirects=True,
    )
    assert svar.status_code == 200
    assert 'role="alert"' in svar.text


def test_get_til_hent_nyeste_er_ikke_lov(klient: TestClient) -> None:
    assert klient.get("/hent-nyeste").status_code == 405


# --- KI-forklaringen gjenbrukes når tallene er uendret (FR-25, AD-7) ---


def test_uendrede_tall_gir_ikke_nytt_kall_til_claude(
    klient: TestClient, klokke: Klokke, claude: FalskClaude
) -> None:
    assert "Skrevet av KI" in klient.get(FRAGMENT).text
    assert claude.kall == 1

    klokke.nå = START + timedelta(minutes=10)
    klient.post("/hent-nyeste", data=SKJEMA)
    fragment = klient.get(FRAGMENT).text
    assert "Skrevet av KI" in fragment
    assert "Hentet 24.11.2026 kl. 13:10." in fragment
    assert claude.kall == 1


def test_endrede_tall_gir_ny_forklaring(
    klient: TestClient,
    klokke: Klokke,
    claude: FalskClaude,
    fhi_mock: respx.MockRouter,
) -> None:
    klient.get(FRAGMENT)
    assert claude.kall == 1

    fhi_mock.routes["data"].respond(json=R1_19)
    klokke.nå = START + timedelta(minutes=10)
    klient.post("/hent-nyeste", data=SKJEMA)
    klient.get(FRAGMENT)
    assert claude.kall == 2
