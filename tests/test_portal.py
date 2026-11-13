"""Pruebas del portal de clientes (/mi) y del ciclo apartado -> entregado -> devuelto."""


def disponible(client, personal, libro_id):
    return client.get(f"/libros/{libro_id}", headers=personal).json()["disponible"]


def test_cliente_solo_ve_sus_prestamos(client, ana):
    r = client.get("/mi/prestamos", headers=ana)
    assert r.status_code == 200
    ids = {p["id"] for p in r.json()}
    assert {"P001", "P003"} <= ids
    assert "P002" not in ids  # es de Luis


def test_cliente_no_puede_usar_endpoints_del_personal(client, ana):
    assert client.get("/prestamos/", headers=ana).status_code == 403
    assert client.get("/usuarios/", headers=ana).status_code == 403
    assert client.post("/libros/", json={"id": "LX01", "editorial_id": "E001", "titulo": "X"},
                       headers=ana).status_code == 403


def test_cliente_puede_ver_catalogo(client, ana):
    r = client.get("/libros/?solo_disponibles=true", headers=ana)
    assert r.status_code == 200
    assert all(libro["disponible"] for libro in r.json())


def test_personal_no_puede_usar_el_portal(client, personal):
    assert client.get("/mi/prestamos", headers=personal).status_code == 403


def test_apartar_entregar_y_devolver(client, ana, personal):
    r = client.post("/mi/prestamos", json={"libros": ["L005"]}, headers=ana)
    assert r.status_code == 201, r.text
    prestamo_id = r.json()["id"]
    try:
        apartado = client.get(f"/prestamos/{prestamo_id}", headers=personal).json()
        assert apartado["estado"] == "APARTADO"
        assert apartado["dias_restantes"] == 3
        assert apartado["usuario_id"] is None
        assert not disponible(client, personal, "L005")

        # Un apartado no se puede "devolver": primero se entrega
        assert client.put(f"/prestamos/{prestamo_id}/devolver",
                          headers=personal).status_code == 409

        assert client.put(f"/prestamos/{prestamo_id}/entregar",
                          headers=personal).status_code == 200
        activo = client.get(f"/prestamos/{prestamo_id}", headers=personal).json()
        assert activo["estado"] == "ACTIVO"
        assert activo["dias_restantes"] == 14
        assert activo["usuario_id"] == "U002"

        # Ya entregado, el cliente ya no lo puede cancelar
        assert client.delete(f"/mi/prestamos/{prestamo_id}", headers=ana).status_code == 409

        assert client.put(f"/prestamos/{prestamo_id}/devolver",
                          headers=personal).status_code == 200
        assert disponible(client, personal, "L005")
    finally:
        client.delete(f"/prestamos/{prestamo_id}", headers=personal)


def test_cancelar_apartado_libera_libro(client, ana, luis, personal):
    prestamo_id = client.post("/mi/prestamos", json={"libros": ["L006"]},
                              headers=ana).json()["id"]
    # Otro cliente no puede cancelarlo (ni saber que existe)
    assert client.delete(f"/mi/prestamos/{prestamo_id}", headers=luis).status_code == 404
    assert client.delete(f"/mi/prestamos/{prestamo_id}", headers=ana).status_code == 200
    assert disponible(client, personal, "L006")


def test_cliente_con_vencidos_no_puede_apartar(client, luis):
    r = client.post("/mi/prestamos", json={"libros": ["L005"]}, headers=luis)
    assert r.status_code == 409
    assert "vencidos" in r.json()["detail"]


def test_limite_de_libros_por_cliente(client, ana):
    # Ana ya tiene 2 libros abiertos; 2 + 4 supera el máximo de 5
    r = client.post("/mi/prestamos", json={"libros": ["L001", "L005", "L006", "L002"]},
                    headers=ana)
    assert r.status_code == 409
    assert "hasta 5" in r.json()["detail"]
