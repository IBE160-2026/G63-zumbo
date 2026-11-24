"""Tester for mellomlagringen (story 2.6, AD-4, FR-7, FR-8).

Alle tester bruker `tmp_path` som cachemappe.
"""

import json
import os
import shutil
from datetime import UTC, datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import pytest

from backend import mellomlager
from backend.domene import Utvalg
from backend.mellomlager import Lagret

FIXTURES = Path(__file__).parent / "fixtures"
DATAFIL = FIXTURES / "fhi" / "724-influensa-2025-2026-alle-nonstl.json"
DIMENSJONSFIL = FIXTURES / "fhi" / "724-dimensjoner.json"
UTVALG = Utvalg(1, "influensa", "2025/2026", "alle")
HENTET = datetime(2026, 11, 23, 21, 20, 15, tzinfo=UTC)
SVAR: dict[str, Any] = json.loads(DATAFIL.read_text(encoding="utf-8"))["svar"]


# --- Lagring og lesing ---


def test_lagre_og_lese_svar(tmp_path: Path) -> None:
    mellomlager.lagre_svar(tmp_path, UTVALG, SVAR, HENTET)
    assert mellomlager.les_svar(tmp_path, UTVALG) == Lagret(HENTET, SVAR)


def test_filen_heter_etter_utvalg_noekkel(tmp_path: Path) -> None:
    mellomlager.lagre_svar(tmp_path, UTVALG, SVAR, HENTET)
    fil = tmp_path / "fhi" / "mal1-influensa-2025-2026-alle.json"
    assert fil.is_file()
    assert [p.name for p in (tmp_path / "fhi").iterdir()] == [fil.name]


def test_filformatet_er_som_fixturene(tmp_path: Path) -> None:
    mellomlager.lagre_svar(tmp_path, UTVALG, SVAR, HENTET)
    innhold = json.loads(mellomlager.svarfil(tmp_path, UTVALG).read_text("utf-8"))
    assert innhold == json.loads(DATAFIL.read_text(encoding="utf-8"))
    assert innhold["hentet"] == "2026-11-23T21:20:15Z"


def test_fixturene_kan_leses_som_cachefiler(tmp_path: Path) -> None:
    (tmp_path / "fhi").mkdir()
    shutil.copy(DATAFIL, mellomlager.svarfil(tmp_path, UTVALG))
    shutil.copy(DIMENSJONSFIL, mellomlager.dimensjonsfil(tmp_path, 724))
    assert mellomlager.les_svar(tmp_path, UTVALG) == Lagret(HENTET, SVAR)
    lagret = mellomlager.les_dimensjoner(tmp_path, 724)
    assert lagret is not None and lagret.hentet == HENTET


def test_lagre_og_lese_dimensjoner(tmp_path: Path) -> None:
    svar = json.loads(DIMENSJONSFIL.read_text(encoding="utf-8"))["svar"]
    mellomlager.lagre_dimensjoner(tmp_path, 724, svar, HENTET)
    assert (tmp_path / "fhi" / "724-dimensjoner.json").is_file()
    assert mellomlager.les_dimensjoner(tmp_path, 724) == Lagret(HENTET, svar)


def test_hentet_lagres_i_utc_og_leses_med_tidssone(tmp_path: Path) -> None:
    norsk = datetime(2026, 11, 23, 22, 20, 15, 999, tzinfo=timezone(timedelta(hours=1)))
    mellomlager.lagre_svar(tmp_path, UTVALG, SVAR, norsk)
    tekst = json.loads(mellomlager.svarfil(tmp_path, UTVALG).read_text("utf-8"))
    assert tekst["hentet"] == "2026-11-23T21:20:15Z"
    lagret = mellomlager.les_svar(tmp_path, UTVALG)
    assert lagret is not None
    assert lagret.hentet == HENTET
    assert lagret.hentet.tzinfo == UTC


def test_ny_lagring_erstatter_den_gamle(tmp_path: Path) -> None:
    mellomlager.lagre_svar(tmp_path, UTVALG, {"gammel": 1}, HENTET)
    senere = HENTET + timedelta(days=1)
    mellomlager.lagre_svar(tmp_path, UTVALG, SVAR, senere)
    assert mellomlager.les_svar(tmp_path, UTVALG) == Lagret(senere, SVAR)


def test_ulike_utvalg_har_hver_sin_fil(tmp_path: Path) -> None:
    annet = Utvalg(1, "influensa", "2025/2026", "80+")
    mellomlager.lagre_svar(tmp_path, UTVALG, SVAR, HENTET)
    mellomlager.lagre_svar(tmp_path, annet, {"annet": True}, HENTET)
    assert mellomlager.les_svar(tmp_path, UTVALG) == Lagret(HENTET, SVAR)
    assert mellomlager.les_svar(tmp_path, annet) == Lagret(HENTET, {"annet": True})


def test_norske_tegn_bevares(tmp_path: Path) -> None:
    svar = {"label": "Påvisninger", "aldersgruppe": "80+ år"}
    mellomlager.lagre_svar(tmp_path, UTVALG, svar, HENTET)
    lagret = mellomlager.les_svar(tmp_path, UTVALG)
    assert lagret is not None and lagret.svar == svar


# --- Atomisk skriving ---


def test_skriving_går_via_midlertidig_fil_og_os_replace(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    kall: list[tuple[Path, Path]] = []
    ekte_replace = os.replace

    def replace(fra: str, til: str) -> None:
        kall.append((Path(fra), Path(til)))
        assert json.loads(Path(fra).read_text("utf-8"))["svar"] == SVAR
        ekte_replace(fra, til)

    monkeypatch.setattr(mellomlager.os, "replace", replace)
    mellomlager.lagre_svar(tmp_path, UTVALG, SVAR, HENTET)
    ((fra, til),) = kall
    assert til == mellomlager.svarfil(tmp_path, UTVALG)
    assert fra.parent == til.parent and fra.name.endswith(".tmp")
    assert not fra.exists()


def test_feil_under_skriving_beholder_den_gamle_fila(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    mellomlager.lagre_svar(tmp_path, UTVALG, SVAR, HENTET)

    def feiler(fra: str, til: str) -> None:
        raise OSError("disken er full")

    monkeypatch.setattr(mellomlager.os, "replace", feiler)
    with pytest.raises(OSError):
        mellomlager.lagre_svar(tmp_path, UTVALG, {"ny": 1}, HENTET)
    assert mellomlager.les_svar(tmp_path, UTVALG) == Lagret(HENTET, SVAR)
    assert [p.name for p in (tmp_path / "fhi").iterdir()] == [
        "mal1-influensa-2025-2026-alle.json"
    ]


# --- Filer som ikke kan leses ---


def test_fil_som_mangler_gir_none(tmp_path: Path) -> None:
    assert mellomlager.les_svar(tmp_path, UTVALG) is None
    assert mellomlager.les_dimensjoner(tmp_path / "finnes-ikke", 724) is None


ØDELAGT: dict[str, bytes] = {
    "tom": b"",
    "halv": b'{"hentet": "2026-11-23T21:20:15Z", "svar": {"a"',
    "ikke-json": b"<html>",
    "ikke-utf8": b'{"hentet": "\xff", "svar": {}}',
    "liste": b"[1, 2]",
    "mangler-svar": b'{"hentet": "2026-11-23T21:20:15Z"}',
    "mangler-hentet": b'{"svar": {}}',
    "ekstra-felt": b'{"hentet": "2026-11-23T21:20:15Z", "svar": {}, "x": 1}',
    "svar-er-liste": b'{"hentet": "2026-11-23T21:20:15Z", "svar": [1]}',
    "hentet-er-tall": b'{"hentet": 1, "svar": {}}',
    "hentet-uten-tidssone": b'{"hentet": "2026-11-23T21:20:15", "svar": {}}',
    "hentet-utenfor-grensene": b'{"hentet": "0001-01-01T00:30:00+01:00", "svar": {}}',
    "hentet-ugyldig": '{"hentet": "i går", "svar": {}}'.encode(),
    "dypt-nøstet": b'{"hentet": "2026-11-23T21:20:15Z", "svar": {"a": '
    + b"[" * 100_000
    + b"]" * 100_000
    + b"}}",
}


@pytest.mark.parametrize("innhold", ØDELAGT.values(), ids=list(ØDELAGT))
def test_ødelagt_fil_regnes_som_ikke_funnet(tmp_path: Path, innhold: bytes) -> None:
    fil = mellomlager.svarfil(tmp_path, UTVALG)
    fil.parent.mkdir(parents=True)
    fil.write_bytes(innhold)
    assert mellomlager.les_svar(tmp_path, UTVALG) is None


def test_mappe_i_stedet_for_fil_regnes_som_ikke_funnet(tmp_path: Path) -> None:
    mellomlager.svarfil(tmp_path, UTVALG).mkdir(parents=True)
    assert mellomlager.les_svar(tmp_path, UTVALG) is None


@pytest.mark.skipif(
    not hasattr(os, "geteuid") or os.geteuid() == 0,
    reason="root kan lese alt, og Windows har ikke chmod 0",
)
def test_fil_uten_lesetilgang_regnes_som_ikke_funnet(tmp_path: Path) -> None:
    mellomlager.lagre_svar(tmp_path, UTVALG, SVAR, HENTET)
    fil = mellomlager.svarfil(tmp_path, UTVALG)
    fil.chmod(0)
    try:
        assert mellomlager.les_svar(tmp_path, UTVALG) is None
    finally:
        fil.chmod(0o644)


# --- Ugyldige argumenter ---


def test_hentet_uten_tidssone_avvises(tmp_path: Path) -> None:
    with pytest.raises(ValueError):
        mellomlager.lagre_svar(tmp_path, UTVALG, SVAR, datetime(2026, 11, 23))
    assert not (tmp_path / "fhi").exists() or not any((tmp_path / "fhi").iterdir())


def test_svar_må_være_et_objekt(tmp_path: Path) -> None:
    with pytest.raises(TypeError):
        mellomlager.lagre_svar(tmp_path, UTVALG, [1, 2], HENTET)  # type: ignore[arg-type]


@pytest.mark.parametrize("tabell", [999, "724", "../x", True])
def test_ukjent_tabell_avvises(tmp_path: Path, tabell: object) -> None:
    with pytest.raises(ValueError):
        mellomlager.les_dimensjoner(tmp_path, tabell)  # type: ignore[arg-type]


def test_manipulert_utvalg_gir_ikke_filnavn(tmp_path: Path) -> None:
    with pytest.raises(ValueError):
        mellomlager.les_svar(tmp_path, Utvalg(1, "../x", "2025/2026"))


# --- Bare mellomlager skriver filer ---


def test_bare_mellomlager_skriver_filer() -> None:
    src = Path(mellomlager.__file__).parent
    treff = [
        str(fil.relative_to(src))
        for fil in src.rglob("*.py")
        if any(
            ord_ in fil.read_text(encoding="utf-8")
            for ord_ in (
                "os.replace",
                "os.rename",
                "write_text",
                "write_bytes",
                "mkstemp",
                "mkdir(",
                "open(",
                "shutil",
            )
        )
    ]
    assert treff == ["mellomlager.py"]


# --- KI-forklaringer (story 4.4, AD-7) ---

NØKKEL = "a" * 64
LAGET = datetime(2026, 11, 24, 12, 30, tzinfo=timezone(timedelta(hours=1)))


def test_lagre_og_lese_forklaring(tmp_path: Path) -> None:
    mellomlager.lagre_forklaring(tmp_path, NØKKEL, LAGET, "claude-haiku-5-5", "Tæxt.")
    lagret = mellomlager.les_forklaring(tmp_path, NØKKEL)
    assert lagret == mellomlager.LagretForklaring(
        LAGET.astimezone(UTC), "claude-haiku-5-5", "Tæxt."
    )
    assert lagret is not None and lagret.laget.tzinfo is UTC


def test_forklaringen_ligger_i_ki_mappen_med_tre_felt(tmp_path: Path) -> None:
    mellomlager.lagre_forklaring(tmp_path, NØKKEL, LAGET, "m", "Tekst.")
    fil = tmp_path / "ki" / f"{NØKKEL}.json"
    assert mellomlager.forklaringsfil(tmp_path, NØKKEL) == fil
    assert json.loads(fil.read_text(encoding="utf-8")) == {
        "laget": "2026-11-24T11:30:00Z",
        "modell": "m",
        "tekst": "Tekst.",
    }


def test_forklaring_som_mangler_gir_none(tmp_path: Path) -> None:
    assert mellomlager.les_forklaring(tmp_path, NØKKEL) is None


@pytest.mark.parametrize(
    "innhold",
    [
        "ikke json",
        "[]",
        '{"laget": "2026-11-24T11:30:00Z", "modell": "m"}',
        '{"laget": "2026-11-24T11:30:00Z", "modell": "m", "tekst": "T", "x": 1}',
        '{"laget": "2026-11-24T11:30:00Z", "modell": " ", "tekst": "T"}',
        '{"laget": "2026-11-24T11:30:00", "modell": "m", "tekst": "T"}',
        '{"laget": "i går", "modell": "m", "tekst": "T"}',
        '{"laget": "2026-11-24T11:30:00Z", "modell": 1, "tekst": "T"}',
        '{"laget": "2026-11-24T11:30:00Z", "modell": "m", "tekst": null}',
        '{"laget": "2026-11-24T11:30:00Z", "modell": "m", "tekst": "  "}',
    ],
)
def test_ødelagt_forklaring_regnes_som_ikke_funnet(
    tmp_path: Path, innhold: str
) -> None:
    fil = mellomlager.forklaringsfil(tmp_path, NØKKEL)
    fil.parent.mkdir(parents=True)
    fil.write_text(innhold, encoding="utf-8")
    assert mellomlager.les_forklaring(tmp_path, NØKKEL) is None


@pytest.mark.parametrize(
    "nøkkel", ["", "A" * 64, "a" * 63, "a" * 65, "../" + "a" * 61, None, 123]
)
def test_ugyldig_forklaringsnøkkel_avvises(tmp_path: Path, nøkkel: object) -> None:
    with pytest.raises(ValueError):
        mellomlager.forklaringsfil(tmp_path, nøkkel)  # type: ignore[arg-type]
    with pytest.raises(ValueError):
        mellomlager.les_forklaring(tmp_path, nøkkel)  # type: ignore[arg-type]


@pytest.mark.parametrize(
    ("nøkkel", "modell", "tekst"),
    [
        (NØKKEL, "m", " "),
        (NØKKEL, "", "T"),
        (NØKKEL, None, "T"),
        (NØKKEL, "m", None),
        ("../" + "a" * 61, "m", "T"),
    ],
)
def test_ugyldig_forklaring_lagres_ikke(
    tmp_path: Path, nøkkel: str, modell: Any, tekst: Any
) -> None:
    with pytest.raises(ValueError):
        mellomlager.lagre_forklaring(tmp_path, nøkkel, LAGET, modell, tekst)
    assert list(tmp_path.rglob("*")) == []


def test_laget_uten_tidssone_avvises(tmp_path: Path) -> None:
    with pytest.raises(ValueError):
        mellomlager.lagre_forklaring(
            tmp_path, NØKKEL, datetime(2026, 11, 24, 12, 0), "m", "T"
        )


def test_forklaringen_skrives_atomisk(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    mellomlager.lagre_forklaring(tmp_path, NØKKEL, LAGET, "m", "Gammel.")

    def feiler(fra: str, til: str) -> None:
        raise OSError("disken er full")

    monkeypatch.setattr(mellomlager.os, "replace", feiler)
    with pytest.raises(OSError):
        mellomlager.lagre_forklaring(tmp_path, NØKKEL, LAGET, "m", "Ny.")
    lagret = mellomlager.les_forklaring(tmp_path, NØKKEL)
    assert lagret is not None and lagret.tekst == "Gammel."
    assert [p.name for p in (tmp_path / "ki").iterdir()] == [f"{NØKKEL}.json"]
