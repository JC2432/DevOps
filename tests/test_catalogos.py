"""CRUD de categorías y clientes, y consulta de autores."""


def test_crud_categoria(client, personal):
    client.delete("/categorias/CT01", headers=personal)
    assert client.post("/categorias/", json={"id": "CT01", "nombre": "Poesía"},
                       headers=personal).status_code == 201
    try:
        assert client.post("/categorias/", json={"id": "CT01", "nombre": "Otra"},
                           headers=personal).status_code == 409
        assert client.put("/categorias/CT01", json={"nombre": "Poesía moderna"},
                          headers=personal).status_code == 200
        categoria = client.get("/categorias/CT01", headers=personal).json()
        assert categoria == {"id": "CT01", "nombre": "Poesía moderna"}
    finally:
        assert client.delete("/categorias/CT01", headers=personal).status_code == 200
    assert client.get("/categorias/CT01", headers=personal).status_code == 404
    assert client.put("/categorias/CT01", json={"nombre": "X"}, headers=personal).status_code == 404


def test_categoria_en_uso_no_se_borra(client, personal):
    # C003 (Tecnología) está asignada a L001 y L005
    assert client.delete("/categorias/C003", headers=personal).status_code == 409


def test_crud_cliente_con_acceso_al_portal(client, personal):
    nuevo = {"id": "CT01", "nombre": "Prueba", "apellido_p": "Cliente",
             "correo": "prueba@example.com", "telefono": "81 1234 5678", "password": "clave123"}
    client.delete("/clientes/CT01", headers=personal)
    assert client.post("/clientes/", json=nuevo, headers=personal).status_code == 201
    try:
        cliente = client.get("/clientes/CT01", headers=personal).json()
        assert cliente["acceso_portal"] is True
        assert "password" not in cliente

        login = {"username": "prueba@example.com", "password": "clave123", "cargo": "CLIENTE"}
        assert client.post("/login", json=login).status_code == 200

        # Cambiar la contraseña desde el panel del personal
        assert client.put("/clientes/CT01", json={"password": "nueva456"},
                          headers=personal).status_code == 200
        assert client.post("/login", json=login).status_code == 401

        # Correo repetido
        assert client.put("/clientes/CT01", json={"correo": "ana@example.com"},
                          headers=personal).status_code == 409
    finally:
        assert client.delete("/clientes/CT01", headers=personal).status_code == 200


def test_cliente_sin_password_no_entra_al_portal(client, personal):
    nuevo = {"id": "CT02", "nombre": "Sin", "apellido_p": "Acceso", "correo": "sin@example.com"}
    client.delete("/clientes/CT02", headers=personal)
    assert client.post("/clientes/", json=nuevo, headers=personal).status_code == 201
    try:
        assert client.get("/clientes/CT02", headers=personal).json()["acceso_portal"] is False
        r = client.post("/login", json={"username": "sin@example.com", "password": "loquesea",
                                        "cargo": "CLIENTE"})
        assert r.status_code == 401
    finally:
        client.delete("/clientes/CT02", headers=personal)


def test_autores(client, ana):
    autores = client.get("/autores/", headers=ana).json()
    assert autores[0]["id"] == "A001" and autores[0]["nacionalidad"] == "Mexicana"
    assert client.get("/autores/A001", headers=ana).json()["apellido_p"] == "Rulfo"
    assert client.get("/autores/ZZZZ", headers=ana).status_code == 404


def test_cargos_para_formulario(client, personal):
    cargos = client.get("/usuarios/cargos", headers=personal).json()
    assert {c["puesto"] for c in cargos} == {"ADMINISTRADOR", "BIBLIOTECARIO"}
