"""Fixtures compartidas. Las pruebas de integración requieren MySQL con schema.sql + seed.sql."""

import pytest
from fastapi.testclient import TestClient

from backend.app.main import app


@pytest.fixture(scope="session")
def client():
    return TestClient(app)


def _iniciar_sesion(client, username, password, cargo):
    r = client.post("/login", json={"username": username, "password": password, "cargo": cargo})
    assert r.status_code == 200, r.text
    return {"Authorization": f"Bearer {r.json()['token']}"}


@pytest.fixture(scope="session")
def personal(client):
    """Headers de sesión de un bibliotecario (usuario de seed.sql)."""
    return _iniciar_sesion(client, "biblio_db", "biblio123", "BIBLIOTECARIO")


@pytest.fixture(scope="session")
def ana(client):
    """Cliente C001: tiene un préstamo vigente (P001) y un apartado (P003)."""
    return _iniciar_sesion(client, "ana@example.com", "cliente123", "CLIENTE")


@pytest.fixture(scope="session")
def luis(client):
    """Cliente C002: tiene un préstamo vencido (P002)."""
    return _iniciar_sesion(client, "luis@example.com", "cliente123", "CLIENTE")
