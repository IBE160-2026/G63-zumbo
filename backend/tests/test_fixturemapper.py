"""Sjekker at fixture-mappene fra AD-10 finnes."""

from pathlib import Path

import pytest

FIXTURES = Path(__file__).parent / "fixtures"


@pytest.mark.parametrize("mappe", ["fhi", "ki", "konstruert"])
def test_fixturemappe_finnes(mappe: str) -> None:
    assert (FIXTURES / mappe).is_dir()
