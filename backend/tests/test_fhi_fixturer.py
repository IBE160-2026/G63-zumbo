"""Sjekker de lagrede svarene fra FHI for tabell 724 (story 1.3, AD-4, AD-10)."""

import json
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest

FHI = Path(__file__).parent / "fixtures" / "fhi"
DATA = FHI / "724-influensa-2025-2026-alle-nonstl.json"
DIMENSJONER = FHI / "724-dimensjoner.json"


def _les(fil: Path) -> dict:
    return json.loads(fil.read_text(encoding="utf-8"))


@pytest.mark.parametrize("fil", [DATA, DIMENSJONER], ids=lambda f: f.name)
def test_fixturen_har_cacheformatet(fil: Path) -> None:
    innhold = _les(fil)
    assert set(innhold) == {"hentet", "svar"}
    hentet = datetime.fromisoformat(innhold["hentet"])
    assert hentet.utcoffset() == timedelta(0), "hentet skal være i UTC"
    assert hentet <= datetime.now(UTC)
    assert innhold["svar"]


def test_dataene_har_uke_2025_w40() -> None:
    svar = _les(DATA)["svar"]
    uker = svar["dimension"]["dateusedforstatistics"]["category"]["index"]
    assert "2025-w40" in uker


def test_dataene_er_utvalget_fra_storyen() -> None:
    svar = _les(DATA)["svar"]
    dimensjon = svar["dimension"]

    def koder(navn: str) -> list[str]:
        return list(dimensjon[navn]["category"]["index"])

    uker = koder("dateusedforstatistics")
    assert uker[0] == "2025-w40"
    assert uker[-1] == "2026-w20"
    assert koder("aldersgruppe") == ["Alle"]
    assert koder("surveillancetype") == ["NONSTL"]
    assert koder("influenzatypeandsubtype") == ["A+B"]
    assert koder("MEASURE_TYPE") == ["Detections", "Tests", "pos_rate"]
    # Én verdi per uke og måltall.
    assert len(svar["value"]) == len(uker) * 3


def test_dimensjonslisten_har_ukene_i_sesongen() -> None:
    svar = _les(DIMENSJONER)["svar"]
    ukedimensjon = next(
        d for d in svar["dimensions"] if d["code"] == "dateusedforstatistics"
    )
    uker = [k["value"] for k in ukedimensjon["categories"]]
    assert "2025-w40" in uker
    assert "2026-w20" in uker
