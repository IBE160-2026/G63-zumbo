"""Sjekker at testene ikke kan nå nettet (NFR-10, AD-10).

`--disable-socket` er satt i `pyproject.toml`. Hvis sperren mangler, får testene
under ingen `SocketBlockedError` og feiler.
"""

import socket

import httpx
import pytest
from pytest_socket import SocketBlockedError

# pytest-socket varsler hver gang en test prøver nettet. Her er det meningen.
pytestmark = pytest.mark.filterwarnings("ignore:A test tried to use socket")


def test_socket_blir_stoppet() -> None:
    with pytest.raises(SocketBlockedError):
        socket.socket(socket.AF_INET, socket.SOCK_STREAM)


def test_httpx_kall_til_fhi_blir_stoppet() -> None:
    # Samme vei som appen skal hente data: httpx mot FHIs åpne API. Allerede
    # navneoppslaget (getaddrinfo) blir stoppet, så ingenting går ut på nettet.
    url = "https://statistikk-data.fhi.no/api/open/v1/msis/Table/724/metadata"
    with pytest.raises(SocketBlockedError):
        httpx.get(url, timeout=1)
