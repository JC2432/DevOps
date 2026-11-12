from fastapi.testclient import TestClient

from backend.app.main import app

client = TestClient(app)


def test_listar_editoriales():
    response = client.get("/editoriales/")
    assert response.status_code == 200
    assert len(response.json()["editoriales"]) >= 1


def test_obtener_editorial():
    response = client.get("/editoriales/E001")
    assert response.status_code == 200
    assert response.json()["EDITORIAL_ID"] == "E001"


def test_editorial_inexistente():
    assert client.get("/editoriales/ZZZZ").status_code == 404
