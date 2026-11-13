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


def test_login_devuelve_token():
    r = client.post("/login", json={"username": "admin_db", "password": "admin123"})
    token = r.json()["token"]
    sesion = client.get("/sesion", headers={"Authorization": f"Bearer {token}"})
    assert sesion.status_code == 200
    assert sesion.json() == {"id": "U001", "rol": "ADMINISTRADOR", "nombre": "Juan"}


def test_login_cliente_con_correo():
    r = client.post(
        "/login",
        json={"username": "ana@example.com", "password": "cliente123", "cargo": "CLIENTE"},
    )
    assert r.status_code == 200
    assert r.json()["rol"] == "CLIENTE"
    assert r.json()["id"] == "C001"


def test_cliente_no_entra_como_personal():
    r = client.post("/login", json={"username": "ana@example.com", "password": "cliente123"})
    assert r.status_code == 401
