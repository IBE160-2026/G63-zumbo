"""Tester for begrepsforklaringene på siden (story 3.6, FR-13, NFR-5).

FHI mockes med `respx`, cachen ligger i `tmp_path`, og klokka er fast. Ingen
test når nettet eller laster `.env`. Lenken fra varselet testes i
`test_web_varsel.py`.
"""

import html as htmlmodul
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
from backend.begreper import BEGREPER
from backend.config import Innstillinger
from backend.domene import Utvalg

FIXTURES = Path(__file__).parent / "fixtures"
DATA_URL = "https://statistikk-data.fhi.no/api/open/v1/msis/Table/724/data"
DIMENSJON_URL = "https://statistikk-data.fhi.no/api/open/v1/msis/Table/724/dimension"
NÅ = datetime(2026, 11, 24, 12, 0, tzinfo=UTC)
HENTET = datetime(2026, 11, 24, 10, 5, tzinfo=UTC)
UTVALG = Utvalg(1, "influensa", "2025/2026", "alle")
STI = "/resultat?mal=1&virus=influensa&sesong=2025/2026&alder=alle"
UTEN_UTVALG = "/resultat?mal=1&virus=influensa&sesong=1999/2000"
"""Resultatsiden med et ugyldig utvalg, så ingen tall vises."""


def _svar(navn: str) -> dict[str, Any]:
    return json.loads((FIXTURES / navn).read_text(encoding="utf-8"))["svar"]


@pytest.fixture
def mappe(tmp_path: Path) -> Path:
    return tmp_path / "cache"


@pytest.fixture
def klient(mappe: Path) -> Iterator[TestClient]:
    with respx.mock(assert_all_called=False) as router:
        router.get(DIMENSJON_URL).respond(json=_svar("fhi/724-dimensjoner.json"))
        router.post(DATA_URL).respond(
            json=_svar("fhi/724-influensa-2025-2026-alle-nonstl.json")
        )
        innstillinger = Innstillinger(None, "modell", mappe)
        app = web.lag_app(lambda: innstillinger, klokke=lambda: NÅ)
        with TestClient(app) as testklient:
            yield testklient


def _forklaringer(html: str) -> list[tuple[str, str, str]]:
    """(id, navn, tekst) for hver `<details>` i begrepsdelen."""
    del_ = re.search(r'<section class="begreper"(.*?)</section>', html, re.DOTALL)
    assert del_, "siden mangler begrepsforklaringene"
    return [
        (id_, htmlmodul.unescape(navn), htmlmodul.unescape(tekst))
        for id_, navn, tekst in re.findall(
            r'<details id="([^"]+)">\s*<summary>(.*?)</summary>\s*<p>(.*?)</p>\s*'
            r"</details>",
            del_[1],
            re.DOTALL,
        )
    ]


def test_siden_viser_alle_sju_forklaringene_ordrett(
    klient: TestClient, mappe: Path
) -> None:
    mellomlager.lagre_svar(
        mappe, UTVALG, _svar("fhi/724-influensa-2025-2026-alle-nonstl.json"), HENTET
    )
    html = klient.get(STI).text
    assert _forklaringer(html) == [(b.html_id, b.navn, b.tekst) for b in BEGREPER]
    assert '<h2 id="begrepstittel">Hva betyr ordene?</h2>' in html


def test_forklaringene_er_lukket_og_bruker_details_og_summary(
    klient: TestClient,
) -> None:
    """`<details>`/`<summary>` åpnes med mus, Enter og mellomrom uten
    JavaScript (NFR-5, AD-8). De er lukket når siden lastes."""
    html = klient.get(UTEN_UTVALG).text
    assert html.count("<details") == len(BEGREPER) == 7
    assert html.count("<summary>") == 7
    assert "<details open" not in html


def test_forklaringene_vises_også_uten_utvalg(klient: TestClient) -> None:
    assert len(_forklaringer(klient.get(UTEN_UTVALG).text)) == 7


def test_forklaringene_står_under_tabellen_og_kilden(
    klient: TestClient, mappe: Path
) -> None:
    mellomlager.lagre_svar(
        mappe, UTVALG, _svar("fhi/724-influensa-2025-2026-alle-nonstl.json"), HENTET
    )
    html = klient.get(STI).text
    assert html.index('<p class="kilde">') < html.index('<section class="begreper"')
