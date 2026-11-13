from backend.app.database import get_connection


def _password_en_bd(usuario_id):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT PASSWORD FROM USUARIOS WHERE USUARIO_ID = %s", (usuario_id,))
        return cursor.fetchone()[0]
    finally:
        conn.close()


def test_password_se_guarda_hasheada_y_no_se_expone(client, personal):
    datos = {
        "id": "UT01", "cargo_id": "R002", "username": "usuario_test",
        "password": "secreto123", "nombre": "Test", "apellido_p": "Prueba",
    }
    client.delete("/usuarios/UT01", headers=personal)  # por si quedó de una corrida anterior
    assert client.post("/usuarios/", json=datos, headers=personal).status_code == 201
    try:
        assert _password_en_bd("UT01") != "secreto123"
        publico = client.get("/usuarios/UT01", headers=personal).json()
        assert "PASSWORD" not in publico and "password" not in publico

        # El nuevo usuario puede iniciar sesión
        login = client.post("/login", json={"username": "usuario_test", "password": "secreto123"})
        assert login.status_code == 200
    finally:
        client.delete("/usuarios/UT01", headers=personal)


def test_username_repetido_devuelve_409(client, personal):
    datos = {
        "id": "UT02", "cargo_id": "R002", "username": "biblio_db",
        "password": "secreto123", "nombre": "Test", "apellido_p": "Prueba",
    }
    assert client.post("/usuarios/", json=datos, headers=personal).status_code == 409


def test_cargo_inexistente_devuelve_400(client, personal):
    datos = {
        "id": "UT03", "cargo_id": "ZZZZ", "username": "otro_test",
        "password": "secreto123", "nombre": "Test", "apellido_p": "Prueba",
    }
    assert client.post("/usuarios/", json=datos, headers=personal).status_code == 400


def test_no_puede_eliminarse_a_si_mismo(client, personal):
    assert client.delete("/usuarios/U002", headers=personal).status_code == 400
