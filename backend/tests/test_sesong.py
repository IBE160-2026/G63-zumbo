"""Tester for sesonger, ISO-uker og utdaterte tall (story 2.3, FR-3, FR-7, AD-5)."""

import ast
import sys
from datetime import UTC, date, datetime, timedelta, timezone
from itertools import pairwise
from pathlib import Path

import pytest

from backend import sesong

# --- Ukene i en sesong ---


def test_sesong_2026_2027_har_uke_53_som_vanlig_uke() -> None:
    uker = sesong.uker("2026/2027")
    assert uker[0] == (2026, 40)
    assert uker[-1] == (2027, 20)
    assert uker[12:15] == ((2026, 52), (2026, 53), (2027, 1))
    assert len(uker) == 34


def test_sesong_uten_uke_53() -> None:
    uker = sesong.uker("2025/2026")
    assert uker[0] == (2025, 40)
    assert uker[-1] == (2026, 20)
    assert (2025, 53) not in uker
    assert len(uker) == 33


@pytest.mark.parametrize("navn", ["2024/2025", "2025/2026", "2026/2027", "2020/2021"])
def test_ukene_følger_hverandre_uten_hull(navn: str) -> None:
    uker = sesong.uker(navn)
    mandager = [date.fromisocalendar(år, uke, 1) for år, uke in uker]
    assert all(b - a == timedelta(weeks=1) for a, b in pairwise(mandager))
    assert list(uker) == sorted(uker)


def test_sesongstart_er_uke_40() -> None:
    assert sesong.uker("2026/2027")[0] == (2026, 40)
    assert sesong.uker("2026/2027", (2026, 40)) == ((2026, 40),)


@pytest.mark.parametrize(
    ("siste", "antall", "siste_uke"),
    [
        ((2026, 47), 8, (2026, 47)),
        ((2026, 53), 14, (2026, 53)),
        ((2027, 1), 15, (2027, 1)),
        ((2027, 20), 34, (2027, 20)),
        ((2027, 30), 34, (2027, 20)),
    ],
)
def test_sesongen_som_pågår_stopper_ved_siste_publiserte_uke(
    siste: tuple[int, int], antall: int, siste_uke: tuple[int, int]
) -> None:
    uker = sesong.uker("2026/2027", siste)
    assert len(uker) == antall
    assert uker[-1] == siste_uke


def test_siste_publiserte_uke_før_sesongstart_gir_ingen_uker() -> None:
    assert sesong.uker("2026/2027", (2026, 39)) == ()
    assert sesong.uker("2026/2027", (2025, 50)) == ()


@pytest.mark.parametrize(
    "navn", ["2026-2027", "2026/2028", "2027/2026", "26/27", "", " 2026/2027"]
)
def test_ugyldig_sesong_avvises(navn: str) -> None:
    with pytest.raises(ValueError):
        sesong.uker(navn)


def test_uke_som_ikke_finnes_avvises() -> None:
    with pytest.raises(ValueError):
        sesong.uker("2025/2026", (2025, 53))


def test_startår_og_navn() -> None:
    assert sesong.startår("2025/2026") == 2025
    assert sesong.navn(2025) == "2025/2026"


# --- Sesongene fra en dato (reserve i AD-3) ---


def norsk(år: int, måned: int, dag: int, time: int = 12, minutt: int = 0) -> datetime:
    return datetime(år, måned, dag, time, minutt, tzinfo=sesong.NORSK_TID)


@pytest.mark.parametrize(
    ("nå", "siste"),
    [
        (norsk(2026, 11, 24), "2026/2027"),
        (norsk(2027, 3, 1), "2026/2027"),
        (norsk(2027, 5, 20), "2026/2027"),
        (norsk(2026, 7, 1), "2025/2026"),
        (norsk(2025, 10, 1), "2025/2026"),
        (norsk(2025, 9, 28), "2024/2025"),
    ],
)
def test_sesonger_fra_dato(nå: datetime, siste: str) -> None:
    sesonger = sesong.sesonger_fra_dato(nå)
    assert sesonger[0] == "2024/2025"
    assert sesonger[-1] == siste
    år = [sesong.startår(s) for s in sesonger]
    assert år == list(range(2024, år[-1] + 1))


def test_ny_sesong_starter_mandag_i_uke_40_i_norsk_tid() -> None:
    # Mandag i uke 40 i 2026 er 28. september.
    assert date.fromisocalendar(2026, 40, 1) == date(2026, 9, 28)
    før = norsk(2026, 9, 27, 23, 59)
    ved = norsk(2026, 9, 28, 0, 0)
    assert sesong.sesonger_fra_dato(før)[-1] == "2025/2026"
    assert sesong.sesonger_fra_dato(ved)[-1] == "2026/2027"
    # Samme tidspunkt skrevet i UTC: søndag kl. 22:00 UTC er mandag i Norge.
    assert sesong.sesonger_fra_dato(ved.astimezone(UTC))[-1] == "2026/2027"


def test_sesonger_fra_dato_før_første_sesong() -> None:
    assert sesong.sesonger_fra_dato(norsk(2023, 1, 1)) == ("2024/2025",)


def test_sesonger_fra_dato_krever_tidssone() -> None:
    with pytest.raises(ValueError):
        sesong.sesonger_fra_dato(datetime(2026, 11, 24, 12, 0))


# --- Utdaterte tall (FR-7, AD-5) ---

HENTET = datetime(2026, 11, 20, 14, 5, tzinfo=UTC)


@pytest.mark.parametrize(
    ("alder", "utdatert"),
    [
        (timedelta(0), False),
        (timedelta(hours=23, minutes=59), False),
        (timedelta(hours=23, minutes=59, seconds=59, microseconds=999999), False),
        (timedelta(hours=24), True),
        (timedelta(hours=24, microseconds=1), True),
        (timedelta(days=3), True),
    ],
)
def test_grensen_på_24_timer(alder: timedelta, utdatert: bool) -> None:
    assert sesong.er_utdatert(HENTET, HENTET + alder) is utdatert


def test_tidssonen_spiller_ingen_rolle_for_grensen() -> None:
    nå = (HENTET + timedelta(hours=24)).astimezone(timezone(timedelta(hours=1)))
    assert sesong.er_utdatert(HENTET, nå) is True
    nå = (HENTET + timedelta(hours=23, minutes=59)).astimezone(sesong.NORSK_TID)
    assert sesong.er_utdatert(HENTET, nå) is False


def test_hentet_frem_i_tid_er_ferskt() -> None:
    assert sesong.er_utdatert(HENTET, HENTET - timedelta(hours=1)) is False


@pytest.mark.parametrize(
    ("hentet", "nå"),
    [
        (datetime(2026, 11, 20, 14, 5), HENTET),
        (HENTET, datetime(2026, 11, 21, 14, 5)),
    ],
)
def test_er_utdatert_krever_tidssone(hentet: datetime, nå: datetime) -> None:
    with pytest.raises(ValueError):
        sesong.er_utdatert(hentet, nå)


# --- Ren kjerne (AD-1) ---


def _tre() -> ast.Module:
    return ast.parse(Path(sesong.__file__).read_text(encoding="utf-8"))


def test_sesong_importerer_bare_standardbiblioteket_og_domene() -> None:
    moduler: set[str] = set()
    for node in ast.walk(_tre()):
        if isinstance(node, ast.Import):
            moduler |= {a.name for a in node.names}
        elif isinstance(node, ast.ImportFrom):
            assert node.level == 0, "sesong skal ikke ha relative importer"
            moduler.add(node.module or "")
    fra_backend = {m for m in moduler if m.split(".")[0] == "backend"}
    assert fra_backend <= {"backend.domene"}, fra_backend
    andre = {m.split(".")[0] for m in moduler - fra_backend}
    assert andre <= set(sys.stdlib_module_names), andre


def test_sesong_bruker_ikke_klokka() -> None:
    kall = {
        node.attr
        for node in ast.walk(_tre())
        if isinstance(node, ast.Attribute)
        and node.attr in {"now", "today", "utcnow", "time", "monotonic"}
    }
    assert kall == set()
