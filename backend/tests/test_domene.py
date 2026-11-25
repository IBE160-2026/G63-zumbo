"""Tester for domenemodellen (story 2.1, AD-2) og gyldige utvalg (story 2.2)."""

import ast
import dataclasses
import json
import re
import sys
from datetime import UTC, datetime
from pathlib import Path

import pytest

from backend import domene
from backend.domene import UgyldigUtvalg, Uke, Utvalg

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


# Endret 24. november 2026: Irenes beslutning i story 2.4.


def test_flere_positive_enn_tester_gir_andel_over_100_og_usikker_uke() -> None:
    uke = Uke(2025, 40, 100, 200)
    assert uke.andel == 200.0
    assert uke.flere_positive_enn_tester
    assert uke.usikker
    assert not uke.manglende


def test_like_mange_positive_som_tester_er_ikke_usikker() -> None:
    uke = Uke(2025, 40, 100, 100)
    assert uke.andel == 100.0
    assert not uke.flere_positive_enn_tester
    assert not uke.usikker


@pytest.mark.parametrize(
    ("tester", "positive"), [(None, 5), (5, None), (None, None), (0, 0)]
)
def test_flere_positive_enn_tester_er_usann_uten_tall(
    tester: int | None, positive: int | None
) -> None:
    assert not Uke(2025, 40, tester, positive).flere_positive_enn_tester


def test_null_tester_og_positive_over_null_er_flere_positive_enn_tester() -> None:
    uke = Uke(2025, 40, 0, 3)
    assert uke.flere_positive_enn_tester
    assert uke.usikker
    assert uke.andel is None


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


SESONGER = ["2024/2025", "2025/2026", "2026/2027"]
GYLDIG = {"mal": "1", "virus": "influensa", "sesong": "2025/2026", "alder": "0-4"}
# Koder som bare FHI bruker. «Alle» og «80+ år» er også norske etiketter.
FHI_KODER = ["NONSTL", "A+B", "pos_rate", "Ukjent", "724", "729", "731"]


def feilmelding(parametre: dict[str, str], sesonger: list[str] = SESONGER) -> str:
    with pytest.raises(UgyldigUtvalg) as feil:
        Utvalg.fra_parametre(parametre, sesonger)
    return str(feil.value)


# --- Utvalg fra parametre (story 2.2): gyldige utvalg ---


def test_gyldige_parametre_gir_utvalg() -> None:
    assert Utvalg.fra_parametre(GYLDIG, SESONGER) == Utvalg(
        1, "influensa", "2025/2026", "0-4"
    )


@pytest.mark.parametrize("virus", list(domene.VIRUS))
@pytest.mark.parametrize("alder", list(domene.ALDERSGRUPPER))
def test_alle_virus_og_aldersgrupper_godtas(virus: str, alder: str) -> None:
    utvalg = Utvalg.fra_parametre({**GYLDIG, "virus": virus, "alder": alder}, SESONGER)
    assert (utvalg.virus, utvalg.aldersgruppe) == (virus, alder)


@pytest.mark.parametrize("alder", [None, ""])
def test_manglende_alder_gir_alle_aldersgrupper(alder: str | None) -> None:
    parametre = {k: v for k, v in GYLDIG.items() if k != "alder"}
    if alder is not None:
        parametre["alder"] = alder
    utvalg = Utvalg.fra_parametre(parametre, SESONGER)
    assert utvalg.aldersgruppe == "alle"
    assert domene.ALDERSGRUPPER[utvalg.aldersgruppe].etikett == "Alle aldersgrupper"


def test_gyldige_sesonger_kan_være_en_hvilken_som_helst_iterable() -> None:
    utvalg = Utvalg.fra_parametre(GYLDIG, iter(SESONGER))
    assert utvalg.sesong == "2025/2026"


# --- Utvalg fra parametre: ugyldige felt ---


@pytest.mark.parametrize(
    ("felt", "verdi", "starten_av_meldingen"),
    [
        (
            "mal",
            None,
            (
                "Velg en mal: «Vis andel positive tester for influensa i sesongen "
                "2025/2026»."
            ),
        ),
        ("mal", "", "Velg en mal:"),
        ("mal", "2", "Velg en mal:"),
        ("mal", "01", "Velg en mal:"),
        ("mal", " 1", "Velg en mal:"),
        ("mal", "1.0", "Velg en mal:"),
        ("mal", "en", "Velg en mal:"),
        ("virus", None, "Velg et virus: Influensa, RSV eller SARS-CoV-2."),
        ("virus", "Influensa", "Velg et virus:"),
        ("virus", "724", "Velg et virus:"),
        ("sesong", None, "Velg en sesong: 2024/2025, 2025/2026 eller 2026/2027."),
        ("sesong", "2023/2024", "Velg en sesong:"),
        ("sesong", "2025-2026", "Velg en sesong:"),
        ("alder", " ", "Velg en aldersgruppe: Alle aldersgrupper, 0–4 år,"),
        ("alder", "ukjent", "Velg en aldersgruppe"),
        ("alder", "Ukjent", "Velg en aldersgruppe"),
        ("alder", "80+ år", "Velg en aldersgruppe"),
    ],
)
def test_hvert_ugyldige_felt_gir_norsk_melding(
    felt: str, verdi: str | None, starten_av_meldingen: str
) -> None:
    parametre = {k: v for k, v in GYLDIG.items() if k != felt}
    if verdi is not None:
        parametre[felt] = verdi
    melding = feilmelding(parametre)
    assert melding.startswith(starten_av_meldingen)
    assert melding.count("Velg") == 1


@pytest.mark.parametrize(
    ("virus", "sesong", "spørsmål"),
    [
        ("influensa", "2025/2026", "for influensa i sesongen 2025/2026"),
        ("rsv", "2024/2025", "for RSV i sesongen 2024/2025"),
        ("sars-cov-2", "2026/2027", "for SARS-CoV-2 i sesongen 2026/2027"),
        ("ebola", "2025/2026", "for viruset du velger i sesongen 2025/2026"),
        ("influensa", "1999/2000", "for influensa i sesongen du velger"),
    ],
)
def test_meldingen_for_ukjent_mal_viser_spørsmålet_med_gyldige_valg(
    virus: str, sesong: str, spørsmål: str
) -> None:
    """Meldingen viser malen som spørsmål, slik skjemaet gjorde (FR-1), og
    gjentar aldri en ugyldig verdi fra adressen."""
    melding = feilmelding({"mal": "9", "virus": virus, "sesong": sesong})
    assert melding.startswith(f"Velg en mal: «Vis andel positive tester {spørsmål}».")
    assert "ebola" not in melding
    assert "1999/2000" not in melding


def test_ukjent_alder_godtas_ikke() -> None:
    assert "ukjent" not in domene.ALDERSGRUPPER
    feilmelding({**GYLDIG, "alder": "ukjent"})


def test_alle_feil_samles_i_én_melding_i_fast_rekkefølge() -> None:
    melding = feilmelding({"alder": "x"})
    assert melding == (
        "Velg en mal: «Vis andel positive tester for viruset du velger i sesongen "
        "du velger». "
        "Velg et virus: Influensa, RSV eller SARS-CoV-2. "
        "Velg en sesong: 2024/2025, 2025/2026 eller 2026/2027. "
        "Velg en aldersgruppe: Alle aldersgrupper, 0–4 år, 5–14 år, 15–29 år, "
        "30–64 år, 65–79 år eller 80+ år."
    )


def test_sesonger_med_feil_format_eller_dubletter_hoppes_over() -> None:
    sesonger = ["2025/2026", "", "2025-2026", "2025/2027", "2025/2026", "2026/2027"]
    melding = feilmelding({**GYLDIG, "sesong": "2025-2026"}, sesonger)
    assert melding == "Velg en sesong: 2025/2026 eller 2026/2027."
    feilmelding({k: v for k, v in GYLDIG.items() if k != "sesong"}, sesonger)
    assert Utvalg.fra_parametre(GYLDIG, sesonger).nøkkel


def test_gyldige_sesonger_kan_ikke_være_én_tekst() -> None:
    with pytest.raises(TypeError):
        Utvalg.fra_parametre(GYLDIG, "2025/2026")


def test_ingen_gyldige_sesonger() -> None:
    melding = feilmelding(GYLDIG, sesonger=[])
    assert melding == "Det finnes ingen sesonger å velge nå. Prøv igjen senere."


def test_feilen_er_en_valueerror() -> None:
    assert issubclass(UgyldigUtvalg, ValueError)


@pytest.mark.parametrize("felt", ["mal", "virus", "sesong", "alder"])
@pytest.mark.parametrize("verdi", ["../x", "../ZZQ<script>"])
def test_manipulert_verdi_avvises_og_vises_ikke(felt: str, verdi: str) -> None:
    melding = feilmelding({**GYLDIG, felt: verdi})
    assert verdi not in melding
    assert "ZZQ" not in melding and "<" not in melding


def test_meldingene_har_ingen_fhi_koder() -> None:
    meldinger = [feilmelding({**GYLDIG, felt: "x"}) for felt in GYLDIG]
    meldinger += [feilmelding({"alder": "x"}), feilmelding(GYLDIG, sesonger=[])]
    for melding in meldinger:
        for kode in FHI_KODER:
            assert not re.search(rf"(?<!\w){re.escape(kode)}(?!\w)", melding), (
                kode,
                melding,
            )


# --- Utvalg.nøkkel ---


def test_nøkkel_eksempel() -> None:
    utvalg = Utvalg(1, "influensa", "2025/2026", "80+")
    assert utvalg.nøkkel == "mal1-influensa-2025-2026-80pluss"


@pytest.mark.parametrize("virus", list(domene.VIRUS))
@pytest.mark.parametrize("alder", list(domene.ALDERSGRUPPER))
@pytest.mark.parametrize("sesong", SESONGER)
def test_nøkkel_har_bare_trygge_tegn(virus: str, alder: str, sesong: str) -> None:
    nøkkel = Utvalg(1, virus, sesong, alder).nøkkel
    assert re.fullmatch(r"[a-z0-9-]+", nøkkel)
    assert ".." not in nøkkel and "/" not in nøkkel


def test_nøkkel_er_lik_for_like_utvalg() -> None:
    a = Utvalg.fra_parametre(GYLDIG, SESONGER)
    b = Utvalg.fra_parametre(dict(GYLDIG), list(SESONGER))
    assert a == b and a is not b
    assert a.nøkkel == b.nøkkel


def test_nøkkel_er_ulik_for_ulike_utvalg() -> None:
    nøkler = {
        Utvalg(mal, virus, sesong, alder).nøkkel
        for mal in domene.MALER
        for virus in domene.VIRUS
        for sesong in SESONGER
        for alder in domene.ALDERSGRUPPER
    }
    antall = len(domene.MALER) * len(domene.VIRUS) * len(SESONGER)
    assert len(nøkler) == antall * len(domene.ALDERSGRUPPER)


@pytest.mark.parametrize(
    "utvalg",
    [
        Utvalg(1, "../x", "2025/2026"),
        Utvalg(1, "influensa", "../x"),
        Utvalg(1, "influensa", "2025/2026", "../x"),
        Utvalg(1, "influensa", "2025/2026\n"),
        Utvalg(1, "influensa", "2026/2025"),
        Utvalg(2, "influensa", "2025/2026"),
        Utvalg(True, "influensa", "2025/2026"),  # type: ignore[arg-type]
        Utvalg("1", "influensa", "2025/2026"),  # type: ignore[arg-type]
    ],
)
def test_nøkkel_avviser_utvalg_som_ikke_er_gyldige(utvalg: Utvalg) -> None:
    with pytest.raises(ValueError):
        utvalg.nøkkel  # noqa: B018
