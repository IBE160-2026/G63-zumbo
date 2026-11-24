"""Tester for gyldige utvalg fra parametre (story 2.2, FR-4, FR-5, AD-4, AD-9)."""

import re

import pytest

from backend import domene
from backend.domene import UgyldigUtvalg, Utvalg

SESONGER = ["2024/2025", "2025/2026", "2026/2027"]
GYLDIG = {"mal": "1", "virus": "influensa", "sesong": "2025/2026", "alder": "0-4"}
# Koder som bare FHI bruker. «Alle» og «80+ år» er også norske etiketter.
FHI_KODER = ["NONSTL", "A+B", "pos_rate", "Ukjent", "724", "729", "731"]


def feilmelding(parametre: dict[str, str], sesonger: list[str] = SESONGER) -> str:
    with pytest.raises(UgyldigUtvalg) as feil:
        Utvalg.fra_parametre(parametre, sesonger)
    return str(feil.value)


# --- Gyldige utvalg ---


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


# --- Ugyldige felt ---


@pytest.mark.parametrize(
    ("felt", "verdi", "starten_av_meldingen"),
    [
        ("mal", None, "Velg en mal."),
        ("mal", "", "Velg en mal."),
        ("mal", "2", "Velg en mal."),
        ("mal", "01", "Velg en mal."),
        ("mal", " 1", "Velg en mal."),
        ("mal", "en", "Velg en mal."),
        ("virus", None, "Velg et virus: Influensa, RSV eller SARS-CoV-2."),
        ("virus", "Influensa", "Velg et virus:"),
        ("virus", "724", "Velg et virus:"),
        ("sesong", None, "Velg en sesong: 2024/2025, 2025/2026 eller 2026/2027."),
        ("sesong", "2023/2024", "Velg en sesong:"),
        ("sesong", "2025-2026", "Velg en sesong:"),
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


def test_ukjent_alder_godtas_ikke() -> None:
    assert "ukjent" not in domene.ALDERSGRUPPER
    feilmelding({**GYLDIG, "alder": "ukjent"})


def test_alle_feil_samles_i_én_melding() -> None:
    melding = feilmelding({})
    assert melding == (
        "Velg en mal. Velg et virus: Influensa, RSV eller SARS-CoV-2. "
        "Velg en sesong: 2024/2025, 2025/2026 eller 2026/2027."
    )


def test_ingen_gyldige_sesonger() -> None:
    melding = feilmelding(GYLDIG, sesonger=[])
    assert melding == "Det finnes ingen sesonger å velge nå. Prøv igjen senere."


def test_feilen_er_en_valueerror() -> None:
    assert issubclass(UgyldigUtvalg, ValueError)


@pytest.mark.parametrize("felt", ["mal", "virus", "sesong", "alder"])
def test_manipulert_verdi_avvises_og_vises_ikke(felt: str) -> None:
    melding = feilmelding({**GYLDIG, felt: "../x"})
    assert "../x" not in melding
    assert "x" not in melding.split()


def test_meldingene_har_ingen_fhi_koder() -> None:
    meldinger = [
        feilmelding({}),
        feilmelding({**GYLDIG, "alder": "x"}),
        feilmelding(GYLDIG, sesonger=[]),
    ]
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
        Utvalg(2, "influensa", "2025/2026"),
        Utvalg(True, "influensa", "2025/2026"),  # type: ignore[arg-type]
        Utvalg("1", "influensa", "2025/2026"),  # type: ignore[arg-type]
    ],
)
def test_nøkkel_avviser_utvalg_som_ikke_er_gyldige(utvalg: Utvalg) -> None:
    with pytest.raises(ValueError):
        utvalg.nøkkel  # noqa: B018
