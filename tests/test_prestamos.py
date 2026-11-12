"""Pruebas de integración de /prestamos (requieren MySQL con schema.sql + seed.sql)."""

from fastapi.testclient import TestClient

from backend.app.main import app

client = TestClient(app)

NUEVO_PRESTAMO = {
    "estado_prestamos_id": "S001",
    "cliente_id": "C001",
    "usuario_id": "U001",
    "fecha_prestamo": "2026-01-15",
    "libros": [{"LIBRO_ID": "L001"}],
}


def test_obtener_prestamos_devuelve_lista():
    response = client.get("/prestamos/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_prestamo_inexistente_devuelve_404():
    response = client.get("/prestamos/ZZZZ")
    assert response.status_code == 404


def test_crear_prestamo_con_cliente_inexistente_devuelve_400():
    datos = {**NUEVO_PRESTAMO, "cliente_id": "NOPE"}
    response = client.post("/prestamos/", json=datos)
    assert response.status_code == 400


def test_flujo_prestar_devolver_y_eliminar():
    """Prestar marca el libro como no disponible; devolver lo libera."""
    response = client.post("/prestamos/", json=NUEVO_PRESTAMO)
    assert response.status_code == 201
    prestamo_id = response.json()["id"]
    try:
        assert not client.get("/libros/L001").json()["disponible"]

        # El mismo libro no se puede prestar dos veces
        repetido = client.post("/prestamos/", json=NUEVO_PRESTAMO)
        assert repetido.status_code == 400

        detalle = client.get(f"/prestamos/{prestamo_id}").json()
        assert detalle["libros"][0]["LIBRO_ID"] == "L001"

        devuelto = client.put(f"/prestamos/{prestamo_id}/devolver")
        assert devuelto.status_code == 200
        assert client.get("/libros/L001").json()["disponible"]
        assert client.get(f"/prestamos/{prestamo_id}").json()["estado"] == "DEVUELTO"
    finally:
        client.delete(f"/prestamos/{prestamo_id}")

    assert client.get(f"/prestamos/{prestamo_id}").status_code == 404
