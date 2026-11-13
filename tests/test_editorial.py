def test_listar_editoriales(client, personal):
    response = client.get("/editoriales/", headers=personal)
    assert response.status_code == 200
    assert len(response.json()) >= 1


def test_obtener_editorial(client, personal):
    response = client.get("/editoriales/E001", headers=personal)
    assert response.status_code == 200
    assert response.json() == {"id": "E001", "nombre": "Fondo de Cultura Económica"}


def test_editorial_inexistente(client, personal):
    assert client.get("/editoriales/ZZZZ", headers=personal).status_code == 404
