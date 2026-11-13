"""Datos inválidos deben dar 4xx con un mensaje claro, nunca 500."""


def test_sin_sesion_devuelve_401(client):
    assert client.get("/libros/").status_code == 401


def test_token_alterado_devuelve_401(client, personal):
    token = personal["Authorization"] + "x"
    assert client.get("/libros/", headers={"Authorization": token}).status_code == 401


def test_libro_repetido_devuelve_409(client, personal):
    r = client.post("/libros/", json={"id": "L001", "editorial_id": "E001", "titulo": "Otro"},
                    headers=personal)
    assert r.status_code == 409
    assert "repetido" in r.json()["detail"]


def test_libro_con_editorial_inexistente_devuelve_400(client, personal):
    r = client.post("/libros/", json={"id": "LT01", "editorial_id": "ZZZZ", "titulo": "X"},
                    headers=personal)
    assert r.status_code == 400


def test_id_demasiado_largo_devuelve_422(client, personal):
    r = client.post("/libros/", json={"id": "L00001", "editorial_id": "E001", "titulo": "X"},
                    headers=personal)
    assert r.status_code == 422


def test_titulo_vacio_devuelve_422(client, personal):
    r = client.post("/libros/", json={"id": "LT01", "editorial_id": "E001", "titulo": "   "},
                    headers=personal)
    assert r.status_code == 422


def test_correo_invalido_devuelve_422(client, personal):
    r = client.post("/clientes/", json={"id": "CT01", "nombre": "A", "apellido_p": "B",
                                        "correo": "no-es-correo"}, headers=personal)
    assert r.status_code == 422


def test_cliente_con_prestamos_no_se_puede_borrar(client, personal):
    assert client.delete("/clientes/C001", headers=personal).status_code == 409


def test_no_se_cambia_disponibilidad_de_libro_prestado(client, personal):
    # L002 está en el préstamo P001 (activo)
    r = client.put("/libros/L002", json={"disponible": True}, headers=personal)
    assert r.status_code == 409
    assert "P001" in r.json()["detail"]
    # Guardar el formulario sin cambiar la disponibilidad sí se permite
    r = client.put("/libros/L002", json={"titulo": "Pedro Páramo", "disponible": False},
                   headers=personal)
    assert r.status_code == 200


def test_crud_libro_completo(client, personal):
    nuevo = {"id": "LT01", "editorial_id": "E002", "titulo": "Libro de prueba", "anio": 2020}
    client.delete("/libros/LT01", headers=personal)
    assert client.post("/libros/", json=nuevo, headers=personal).status_code == 201
    try:
        r = client.put("/libros/LT01", json={"titulo": "O'Brien & <Cía>"}, headers=personal)
        assert r.status_code == 200
        libro = client.get("/libros/LT01", headers=personal).json()
        assert libro["titulo"] == "O'Brien & <Cía>"
        assert libro["editorial"] == "Planeta"
    finally:
        assert client.delete("/libros/LT01", headers=personal).status_code == 200
