"""Sjekker de lagrede svarene fra FHI for tabell 724, 729 og 731 (story 1.3, 6.1,
6.2, AD-4, AD-10)."""

import json
import math
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest

FHI = Path(__file__).parent / "fixtures" / "fhi"
DATA = FHI / "724-influensa-2025-2026-alle-nonstl.json"
DIMENSJONER = FHI / "724-dimensjoner.json"
RSV_DATA = FHI / "729-rsv-2025-2026-alle-nonstl.json"
RSV_DIMENSJONER = FHI / "729-dimensjoner.json"
SARS_DATA = FHI / "731-sars-cov-2-2025-2026-alle-nonstl.json"
SARS_DIMENSJONER = FHI / "731-dimensjoner.json"


def _les(fil: Path) -> dict:
    return json.loads(fil.read_text(encoding="utf-8"))


def _koder(svar: dict, dimensjon: str) -> list[str]:
    return list(svar["dimension"][dimensjon]["category"]["index"])


def _uker_i_dimensjonslisten() -> list[str]:
    svar = _les(DIMENSJONER)["svar"]
    ukedimensjon = next(
        d for d in svar["dimensions"] if d["code"] == "dateusedforstatistics"
    )
    return [k["value"] for k in ukedimensjon["categories"]]


@pytest.mark.parametrize(
    "fil",
    [DATA, DIMENSJONER, RSV_DATA, RSV_DIMENSJONER, SARS_DATA, SARS_DIMENSJONER],
    ids=lambda f: f.name,
)
def test_fixturen_har_cacheformatet(fil: Path) -> None:
    innhold = _les(fil)
    assert set(innhold) == {"hentet", "svar"}
    hentet = datetime.fromisoformat(innhold["hentet"])
    assert hentet.utcoffset() == timedelta(0), "hentet skal være i UTC"
    assert hentet <= datetime.now(UTC)
    # Rått JSON-svar, ikke en CSV-tekst.
    assert isinstance(innhold["svar"], dict) and innhold["svar"]


def test_dataene_er_json_stat2() -> None:
    svar = _les(DATA)["svar"]
    assert svar["class"] == "dataset"
    assert svar["version"] == "2.0"


def test_dataene_har_uke_2025_w40() -> None:
    svar = _les(DATA)["svar"]
    assert "2025-w40" in _koder(svar, "dateusedforstatistics")
    # Verdiene er flate, uke først og måltall sist: de tre første er uke 40.
    assert svar["value"][:3] == [64, 7023, 0.9112915]


def test_dataene_er_utvalget_fra_storyen() -> None:
    svar = _les(DATA)["svar"]
    assert _koder(svar, "aldersgruppe") == ["Alle"]
    assert _koder(svar, "surveillancetype") == ["NONSTL"]
    assert _koder(svar, "influenzatypeandsubtype") == ["A+B"]
    assert _koder(svar, "MEASURE_TYPE") == ["Detections", "Tests", "pos_rate"]


def test_dataene_har_alle_ukene_i_sesongen() -> None:
    # Alle publiserte uker fra 2025-w40 til 2026-w20, i rekkefølge, uten hull.
    svar = _les(DATA)["svar"]
    alle = _uker_i_dimensjonslisten()
    forventet = alle[alle.index("2025-w40") : alle.index("2026-w20") + 1]
    assert len(forventet) == 33
    assert _koder(svar, "dateusedforstatistics") == forventet


def test_verdiene_følger_id_og_size() -> None:
    svar = _les(DATA)["svar"]
    assert svar["id"][0] == "dateusedforstatistics"
    assert svar["id"][-1] == "MEASURE_TYPE"
    assert svar["size"] == [len(_koder(svar, d)) for d in svar["id"]]
    assert len(svar["value"]) == math.prod(svar["size"])
    # Ingen skjulte verdier i dette svaret (se README).
    assert all(isinstance(v, int | float) for v in svar["value"])


def test_rsv_dataene_er_utvalget_fra_storyen() -> None:
    svar = _les(RSV_DATA)["svar"]
    assert svar["class"] == "dataset" and svar["version"] == "2.0"
    assert _koder(svar, "aldersgruppe") == ["Alle"]
    assert _koder(svar, "surveillancetype") == ["NONSTL"]
    assert _koder(svar, "rsvtype") == ["A+B"]
    assert _koder(svar, "MEASURE_TYPE") == ["Detections", "Tests", "pos_rate"]
    assert svar["size"] == [len(_koder(svar, d)) for d in svar["id"]]
    assert len(svar["value"]) == math.prod(svar["size"])


def test_sars_cov_2_dataene_er_utvalget_fra_storyen() -> None:
    svar = _les(SARS_DATA)["svar"]
    assert svar["class"] == "dataset" and svar["version"] == "2.0"
    # Ingen typedimensjon, og aldersgruppen står foran ukene (README-en).
    assert svar["id"] == [
        "aldersgruppe",
        "dateusedforstatistics",
        "surveillancetype",
        "MEASURE_TYPE",
    ]
    assert _koder(svar, "aldersgruppe") == ["Alle"]
    assert _koder(svar, "surveillancetype") == ["NONSTL"]
    assert _koder(svar, "MEASURE_TYPE") == ["Detections", "Tests", "pos_rate"]
    assert svar["size"] == [len(_koder(svar, d)) for d in svar["id"]]
    assert len(svar["value"]) == math.prod(svar["size"])
