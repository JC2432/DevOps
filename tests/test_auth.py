from fastapi.testclient import TestClient

from backend.app.main import app

client = TestClient(app)


def test_login_correcto():
    r = client.post("/login", json={"username": "admin_db", "password": "admin123"})
    assert r.status_code == 200
    datos = r.json()
    assert datos["username"] == "admin_db"
    assert datos["cargo"] == "ADMINISTRADOR"
    assert "password" not in datos


def test_login_con_cargo_correcto():
    r = client.post(
        "/login",
        json={"username": "biblio_db", "password": "biblio123", "cargo": "bibliotecario"},
    )
    assert r.status_code == 200
    assert r.json()["cargo"] == "BIBLIOTECARIO"


def test_login_cargo_equivocado():
    r = client.post(
        "/login",
        json={"username": "biblio_db", "password": "biblio123", "cargo": "ADMINISTRADOR"},
    )
    assert r.status_code == 401


def test_login_password_incorrecta():
    r = client.post("/login", json={"username": "admin_db", "password": "mala"})
    assert r.status_code == 401


def test_login_usuario_inexistente_mismo_mensaje():
    malo = client.post("/login", json={"username": "no_existe", "password": "x"})
    mala_pw = client.post("/login", json={"username": "admin_db", "password": "x"})
    assert malo.status_code == 401
    assert malo.json() == mala_pw.json()
