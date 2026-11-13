"""Pruebas de integración de /prestamos (vista del personal)."""


def disponible(client, personal, libro_id):
    return client.get(f"/libros/{libro_id}", headers=personal).json()["disponible"]


def test_listar_prestamos_incluye_libros_y_dias(client, personal):
    response = client.get("/prestamos/", headers=personal)
    assert response.status_code == 200
    prestamos = {p["id"]: p for p in response.json()}
    assert prestamos["P001"]["libros"][0]["id"] == "L002"
    assert prestamos["P001"]["dias_restantes"] == 9


def test_prestamo_vencido_se_calcula_por_fecha(client, personal):
    p002 = client.get("/prestamos/P002", headers=personal).json()
    assert p002["estado"] == "VENCIDO"
    assert p002["dias_restantes"] < 0


def test_prestamo_inexistente_devuelve_404(client, personal):
    assert client.get("/prestamos/ZZZZ", headers=personal).status_code == 404


def test_cliente_inexistente_devuelve_400(client, personal):
    r = client.post("/prestamos/", json={"cliente_id": "NOPE", "libros": ["L001"]},
                    headers=personal)
    assert r.status_code == 400


def test_libro_no_disponible_devuelve_409_y_no_deja_nada_a_medias(client, personal):
    antes = len(client.get("/prestamos/", headers=personal).json())
    # L001 está libre pero L002 está prestado: no se debe crear nada ni apartar L001
    r = client.post("/prestamos/", json={"cliente_id": "C001", "libros": ["L001", "L002"]},
                    headers=personal)
    assert r.status_code == 409
    assert "Pedro Páramo" in r.json()["detail"]
    assert len(client.get("/prestamos/", headers=personal).json()) == antes
    assert disponible(client, personal, "L001")


def test_fecha_limite_anterior_devuelve_422(client, personal):
    r = client.post(
        "/prestamos/",
        json={"cliente_id": "C001", "libros": ["L001"],
              "fecha_prestamo": "2026-05-10", "fecha_limite": "2026-05-01"},
        headers=personal,
    )
    assert r.status_code == 422


def test_flujo_prestar_devolver_y_eliminar(client, personal):
    """Prestar marca el libro como no disponible; devolver lo libera una sola vez."""
    r = client.post("/prestamos/", json={"cliente_id": "C001", "libros": ["L001"]},
                    headers=personal)
    assert r.status_code == 201, r.text
    prestamo_id = r.json()["id"]
    try:
        assert not disponible(client, personal, "L001")
        detalle = client.get(f"/prestamos/{prestamo_id}", headers=personal).json()
        assert detalle["estado"] == "ACTIVO"
        assert detalle["usuario_id"] == "U002"
        assert detalle["dias_restantes"] == 14

        # El mismo libro no se puede prestar dos veces
        repetido = client.post("/prestamos/", json={"cliente_id": "C002", "libros": ["L001"]},
                               headers=personal)
        assert repetido.status_code == 409

        assert client.put(f"/prestamos/{prestamo_id}/devolver", headers=personal).status_code == 200
        assert disponible(client, personal, "L001")
        detalle = client.get(f"/prestamos/{prestamo_id}", headers=personal).json()
        assert detalle["estado"] == "DEVUELTO"
        assert detalle["dias_restantes"] is None

        # Devolver dos veces no está permitido
        assert client.put(f"/prestamos/{prestamo_id}/devolver", headers=personal).status_code == 409
    finally:
        client.delete(f"/prestamos/{prestamo_id}", headers=personal)
    assert client.get(f"/prestamos/{prestamo_id}", headers=personal).status_code == 404


def test_borrar_prestamo_devuelto_no_libera_libro_prestado_a_otro(client, personal):
    """Bug anterior: borrar un préstamo viejo marcaba como disponible un libro ya re-prestado."""
    viejo = client.post("/prestamos/", json={"cliente_id": "C001", "libros": ["L001"]},
                        headers=personal).json()["id"]
    client.put(f"/prestamos/{viejo}/devolver", headers=personal)
    nuevo = client.post("/prestamos/", json={"cliente_id": "C002", "libros": ["L001"]},
                        headers=personal).json()["id"]
    try:
        assert client.delete(f"/prestamos/{viejo}", headers=personal).status_code == 200
        assert not disponible(client, personal, "L001")
    finally:
        client.delete(f"/prestamos/{nuevo}", headers=personal)
    assert disponible(client, personal, "L001")


def test_renovar_amplia_fecha_limite(client, personal):
    original = client.get("/prestamos/P001", headers=personal).json()["fecha_limite"]
    try:
        r = client.put("/prestamos/P001", json={"fecha_limite": "2099-01-01"}, headers=personal)
        assert r.status_code == 200
        renovado = client.get("/prestamos/P001", headers=personal).json()
        assert renovado["fecha_limite"] == "2099-01-01"
    finally:
        client.put("/prestamos/P001", json={"fecha_limite": original}, headers=personal)
