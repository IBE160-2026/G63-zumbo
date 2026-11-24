"""Tester for sesonger, ISO-uker og utdaterte tall (story 2.3, FR-3, FR-7, AD-5)."""

import ast
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


def test_sesong_2020_2021_har_også_uke_53() -> None:
    uker = sesong.uker("2020/2021")
    assert (2020, 53) in uker
    assert len(uker) == 34


def test_første_sesong_2024_2025() -> None:
    uker = sesong.uker("2024/2025")
    assert (uker[0], uker[-1], len(uker)) == ((2024, 40), (2025, 20), 33)


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
    "navn",
    [
        "2026-2027",
        "2026/2028",
        "2027/2026",
        "26/27",
        "",
        " 2026/2027",
        "2026/2027\n",
        "２０２６/２０２７",
        None,
        2026,
    ],
)
def test_ugyldig_sesong_avvises(navn: object) -> None:
    with pytest.raises(ValueError):
        sesong.uker(navn)


@pytest.mark.parametrize(
    "uke",
    [(2025, 53), (2026, 0), (2026, 54), (2026,), (2026, 47, 1), 2026, (None, 47)],
)
def test_uke_som_ikke_finnes_avvises(uke: object) -> None:
    with pytest.raises(ValueError, match="uka finnes ikke"):
        sesong.uker("2025/2026", uke)  # type: ignore[arg-type]


@pytest.mark.parametrize("uke", [(True, 40), (2026.0, 47)])
def test_uke_må_være_heltall(uke: object) -> None:
    with pytest.raises(ValueError):
        sesong.uker("2026/2027", uke)  # type: ignore[arg-type]


def test_siste_publiserte_uke_kan_være_en_liste() -> None:
    assert sesong.uker("2026/2027", [2026, 41]) == ((2026, 40), (2026, 41))  # type: ignore[arg-type]


def test_samme_sesongregel_som_utvalg() -> None:
    from backend import domene

    for tekst in ["2025/2026", "2025/2027", "2025-2026", "2025/2026\n"]:
        try:
            sesong.startår(tekst)
            godtatt = True
        except ValueError:
            godtatt = False
        assert godtatt is domene.er_sesong(tekst)


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
        (norsk(2027, 5, 24, 0, 0), "2026/2027"),
        (norsk(2027, 1, 1), "2026/2027"),
        (norsk(2026, 1, 1), "2025/2026"),
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


@pytest.mark.parametrize(
    ("hentet", "nå", "utdatert"),
    [
        # Vintertid starter 25.10.2026: 24 ekte timer er bare 23 på veggklokka.
        (datetime(2026, 10, 24, 12, 0), datetime(2026, 10, 25, 11, 0), True),
        (datetime(2026, 10, 24, 12, 0), datetime(2026, 10, 25, 10, 59), False),
        # Sommertid starter 28.3.2027: 24 ekte timer er 25 på veggklokka.
        (datetime(2027, 3, 27, 12, 0), datetime(2027, 3, 28, 12, 30), False),
        (datetime(2027, 3, 27, 12, 0), datetime(2027, 3, 28, 13, 0), True),
    ],
)
def test_grensen_over_skifte_til_og_fra_sommertid(
    hentet: datetime, nå: datetime, utdatert: bool
) -> None:
    hentet = hentet.replace(tzinfo=sesong.NORSK_TID)
    nå = nå.replace(tzinfo=sesong.NORSK_TID)
    assert sesong.er_utdatert(hentet, nå) is utdatert


@pytest.mark.parametrize(
    ("frem_i_tid", "utdatert"),
    [
        (timedelta(minutes=5), False),
        (timedelta(minutes=5, microseconds=1), True),
        (timedelta(hours=1), True),
        (timedelta(days=30), True),
    ],
)
def test_hentet_frem_i_tid(frem_i_tid: timedelta, utdatert: bool) -> None:
    assert sesong.er_utdatert(HENTET + frem_i_tid, HENTET) is utdatert


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


def test_sesong_importerer_bare_det_den_trenger() -> None:
    moduler: set[str] = set()
    for node in ast.walk(_tre()):
        if isinstance(node, ast.Import):
            moduler |= {a.name for a in node.names}
        elif isinstance(node, ast.ImportFrom):
            assert node.level == 0, "sesong skal ikke ha relative importer"
            moduler.add(node.module or "")
    assert moduler <= {"datetime", "zoneinfo", "backend.domene"}, moduler


KLOKKE_OG_FILER = {"now", "today", "utcnow", "time", "monotonic", "open", "environ"}


def test_sesong_bruker_ikke_klokka_eller_filer() -> None:
    navn = set()
    for node in ast.walk(_tre()):
        if isinstance(node, ast.Attribute):
            navn.add(node.attr)
        elif isinstance(node, ast.Name):
            navn.add(node.id)
        elif isinstance(node, ast.alias):
            navn.add(node.name)
    assert navn & KLOKKE_OG_FILER == set()
