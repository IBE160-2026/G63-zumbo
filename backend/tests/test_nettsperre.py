"""Sjekker at testene ikke kan nå nettet (NFR-10, AD-10).

`--disable-socket` er satt i `pyproject.toml`. Hvis sperren mangler, får testene
under ingen `SocketBlockedError` og feiler.
"""

import socket

import httpx
import pytest
import respx
from pytest_socket import SocketBlockedError

# pytest-socket varsler hver gang en test prøver nettet. Her er det meningen.
pytestmark = pytest.mark.filterwarnings("ignore:A test tried to use socket")

# `.invalid` er reservert og finnes aldri (RFC 2606). Hvis sperren mangler,
# går ingen forespørsel til FHI; testen feiler med ConnectError i stedet.
FHI_URL = "https://statistikk-data.fhi.invalid/api/open/v1/msis/Table/724/metadata"


def test_socket_blir_stoppet() -> None:
    with pytest.raises(SocketBlockedError):
        socket.socket(socket.AF_INET, socket.SOCK_STREAM)


def test_httpx_kall_blir_stoppet() -> None:
    # Samme vei som appen skal hente data fra FHI: httpx. Allerede
    # navneoppslaget (getaddrinfo) blir stoppet.
    with pytest.raises(SocketBlockedError):
        httpx.get(FHI_URL, timeout=1)


@respx.mock
def test_respx_virker_med_sperren_på() -> None:
    # Slik skal FHI mockes i senere tester: respx svarer uten å åpne en socket.
    respx.get(FHI_URL).respond(200, json={"tabell": 724})
    assert httpx.get(FHI_URL).json() == {"tabell": 724}
