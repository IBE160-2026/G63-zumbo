"""Tester for domenemodellen (story 2.1, AD-2)."""

import ast
import dataclasses
import json
import sys
from datetime import UTC, datetime
from pathlib import Path

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


def test_aldersgruppekodene_finnes_hos_fhi() -> None:
    fil = Path(__file__).parent / "fixtures" / "fhi" / "724-dimensjoner.json"
    dimensjoner = json.loads(fil.read_text(encoding="utf-8"))["svar"]["dimensions"]
    (alder,) = [d for d in dimensjoner if d["code"] == "aldersgruppe"]
    (alle,) = alder["categories"]
    koder = {alle["value"]} | {c["value"] for c in alle["children"]}
    assert {g.fhi_kode for g in domene.ALDERSGRUPPER.values()} == koder - {"Ukjent"}


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
    uke = Uke(2025, 50, None, None)
    assert uke.manglende
    assert uke.andel is None


def test_andel_stemmer_med_fhi() -> None:
    # Uke 2025-w40 i fixturen: 64 positive av 7023 tester, pos_rate 0.9112915.
    uke = Uke(2025, 40, 7023, 64)
    assert not uke.manglende
    assert uke.andel == pytest.approx(0.9112915, abs=1e-6)


def test_andel_følger_tallene_etter_replace() -> None:
    uke = dataclasses.replace(Uke(2025, 40, 100, 5), positive=10)
    assert uke.andel == 10.0


def test_null_positive_gir_andel_null_ikke_none() -> None:
    # 0 positive av 100 er en ekte null, ikke en skjult verdi.
    assert Uke(2025, 40, 100, 0).andel == 0.0


def test_null_tester_gir_ingen_andel_men_er_ikke_manglende() -> None:
    uke = Uke(2025, 40, 0, 0)
    assert uke.andel is None
    assert not uke.manglende
    assert uke.usikker


@pytest.mark.parametrize(("år", "ukenummer"), [(2025, 0), (2025, 53), (2026, 54)])
def test_uker_som_ikke_finnes_avvises(år: int, ukenummer: int) -> None:
    with pytest.raises(ValueError):
        Uke(år, ukenummer, 100, 5)


def test_uke_53_godtas_når_året_har_den() -> None:
    assert Uke(2026, 53, 100, 5).ukenummer == 53


@pytest.mark.parametrize(("tester", "positive"), [(-1, 0), (100, -1)])
def test_negative_tall_avvises(tester: int, positive: int) -> None:
    with pytest.raises(ValueError):
        Uke(2025, 40, tester, positive)


# --- Utvalg, Dataserie og Regelutslag ---


def test_utvalg_har_alle_som_standard_og_finner_tabellen() -> None:
    utvalg = domene.Utvalg(mal=1, virus="influensa", sesong="2025/2026")
    assert utvalg.aldersgruppe == "alle"
    assert utvalg.tabell == 724


def test_dataserie_lagrer_ukene_som_tuple() -> None:
    utvalg = domene.Utvalg(1, "rsv", "2025/2026")
    serie = domene.Dataserie(utvalg, [Uke(2025, 40, 100, 5), Uke(2025, 41, None, 2)])
    assert isinstance(serie.uker, tuple)
    assert [u.manglende for u in serie.uker] == [False, True]


def test_regelutslag() -> None:
    utslag = domene.Regelutslag("R2", "6 av 20 uker har færre enn 30 tester")
    assert utslag.regel == "R2"
    with pytest.raises(ValueError):
        domene.Regelutslag("R6", "finnes ikke")
    with pytest.raises(ValueError):
        domene.Regelutslag("R1", " ")


# --- Kildehenvisning ---

HENTET = datetime(2026, 11, 23, 13, 5, tzinfo=UTC)


@pytest.mark.parametrize(
    ("tabell", "kildetekst", "tabellnavn"),
    [
        (
            724,
            (
                "Kilde: MSIS-labdatabase og Referanselaboratoriet for influensa, "
                "Folkehelseinstituttet (FHI)."
            ),
            "RESPIaggr Influensa antall og andel",
        ),
        (
            729,
            (
                "Kilde: MSIS-labdatabase og Referanselaboratoriet for RS-virus, "
                "Folkehelseinstituttet (FHI)."
            ),
            "RESPIaggr RSV antall og andel",
        ),
        (
            731,
            (
                "Kilde: MSIS-labdatabase og Referanselaboratoriet for koronavirus med "
                "utbruddspotensiale, Folkehelseinstituttet (FHI)."
            ),
            "RESPIaggr SARS-CoV-2 antall og andel",
        ),
    ],
)
def test_kildehenvisning(tabell: int, kildetekst: str, tabellnavn: str) -> None:
    # Ordrett fra addendumet (story 1.4) og tabellnavn fra PRD kapittel 4.
    kilde = domene.kildehenvisning(tabell, HENTET)
    assert kilde == domene.Kildehenvisning(kildetekst, tabell, tabellnavn, HENTET)


def test_kildehenvisning_avviser_ukjent_tabell_og_tid_uten_tidssone() -> None:
    with pytest.raises(ValueError):
        domene.kildehenvisning(733, HENTET)
    with pytest.raises(ValueError):
        domene.kildehenvisning(724, datetime(2026, 11, 23, 13, 5))


# --- Ren kjerne (AD-1) ---


def test_domene_importerer_bare_standardbiblioteket() -> None:
    tre = ast.parse(Path(domene.__file__).read_text(encoding="utf-8"))
    moduler: set[str] = set()
    for node in ast.walk(tre):
        if isinstance(node, ast.Import):
            moduler |= {a.name.split(".")[0] for a in node.names}
        elif isinstance(node, ast.ImportFrom):
            assert node.level == 0, "domene skal ikke ha relative importer"
            moduler.add((node.module or "").split(".")[0])
    assert moduler <= set(sys.stdlib_module_names), moduler
    assert "backend" not in moduler
