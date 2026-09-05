from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)


def test_obtener_prestamos():
    """
    Prueba básica del endpoint /prestamos/.
    Requiere que la base de datos MySQL esté disponible (local o CI)
    y que la tabla 'prestamos' exista (ver database/schema.sql).
    """
    response = client.get("/prestamos/")
    assert response.status_code == 200
    assert "prestamos" in response.json()
