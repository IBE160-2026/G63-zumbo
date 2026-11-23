"""Tester for domenemodellen (story 2.1, AD-2)."""

import pytest

from backend import domene
from backend.domene import Uke

# --- Faste lister ---


def test_virus_til_tabell() -> None:
    assert {n: v.tabell for n, v in domene.VIRUS.items()} == {
        "influensa": 724,
        "rsv": 729,
        "sars-cov-2": 731,
    }
    assert all(v.tabell in domene.TABELLER for v in domene.VIRUS.values())


def test_sju_aldersgrupper_med_alle_først_og_uten_ukjent() -> None:
    grupper = list(domene.ALDERSGRUPPER.values())
    assert [g.etikett for g in grupper] == [
        "Alle aldersgrupper",
        "0–4 år",
        "5–14 år",
        "15–29 år",
        "30–64 år",
        "65–79 år",
        "80+ år",
    ]
    assert grupper[0].nøkkel == domene.STANDARD_ALDERSGRUPPE
    assert "Ukjent" not in {g.fhi_kode for g in grupper}


def test_mal_1_finnes() -> None:
    assert list(domene.MALER) == [1]
    assert domene.MALER[1].tittel == "Andel positive tester uke for uke"


def test_listene_kan_ikke_endres() -> None:
    with pytest.raises(TypeError):
        domene.VIRUS["ny"] = domene.VIRUS["rsv"]  # type: ignore[index]


# --- Uke ---


@pytest.mark.parametrize(("tester", "usikker"), [(29, True), (30, False), (0, True)])
def test_usikker_ved_færre_enn_30_tester(tester: int, usikker: bool) -> None:
    assert Uke(2025, 50, tester, 5).usikker is usikker


def test_skjult_antall_tester_er_usikker_og_manglende() -> None:
    uke = Uke(2025, 50, None, 5)
    assert uke.usikker
    assert uke.manglende
    assert uke.andel is None


def test_skjult_antall_positive_er_manglende_men_ikke_usikker() -> None:
    uke = Uke(2025, 50, 100, None)
    assert uke.manglende
    assert not uke.usikker
    assert uke.andel is None


def test_begge_skjult() -> None:
    uke = Uke(2025, 50, None, None, andel=1.5)
    assert uke.manglende
    assert uke.andel is None


def test_andel_fra_fhi_er_none_når_uka_er_manglende() -> None:
    # Selv om FHI skulle sende en andel, er den aldri med for en manglende uke.
    assert Uke(2025, 50, 100, None, andel=0.0).andel is None


def test_andel_regnes_ut_når_den_ikke_er_oppgitt() -> None:
    uke = Uke(2025, 40, 7023, 64)
    assert not uke.manglende
    assert uke.andel == pytest.approx(0.9112915, abs=1e-6)


def test_andel_fra_fhi_beholdes() -> None:
    assert Uke(2025, 40, 7023, 64, andel=0.9112915).andel == 0.9112915


def test_null_positive_gir_andel_null_ikke_none() -> None:
    # 0 positive av 100 er en ekte null, ikke en skjult verdi.
    assert Uke(2025, 40, 100, 0).andel == 0.0


def test_null_tester_gir_ingen_andel() -> None:
    assert Uke(2025, 40, 0, 0).andel is None


@pytest.mark.parametrize("ukenummer", [0, 54])
def test_ugyldig_ukenummer(ukenummer: int) -> None:
    with pytest.raises(ValueError):
        Uke(2025, ukenummer, 100, 5)


def test_negative_tall_avvises() -> None:
    with pytest.raises(ValueError):
        Uke(2025, 40, -1, 0)
