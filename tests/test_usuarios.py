from fastapi.testclient import TestClient

from backend.app.database import get_connection
from backend.app.main import app

client = TestClient(app)


def _password_en_bd(usuario_id):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT PASSWORD FROM USUARIOS WHERE USUARIO_ID = %s", (usuario_id,))
        return cursor.fetchone()[0]
    finally:
        conn.close()


def test_password_se_guarda_hasheada_y_no_se_expone():
    datos = {
        "id": "UT01", "cargo_id": "R002", "username": "usuario_test",
        "password": "secreto123", "nombre": "Test", "apellido_p": "Prueba",
    }
    assert client.post("/usuarios/", json=datos).status_code == 201
    try:
        assert _password_en_bd("UT01") != "secreto123"
        publico = client.get("/usuarios/UT01").json()
        assert "PASSWORD" not in publico and "password" not in publico
    finally:
        client.delete("/usuarios/UT01")
