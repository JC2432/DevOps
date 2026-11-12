from backend.app.seguridad import hash_password, verificar_password


def test_hash_no_guarda_texto_plano():
    hashed = hash_password("secreto123")
    assert "secreto123" not in hashed
    assert len(hashed) < 255  # cabe en VARCHAR(255)


def test_verificar_password():
    hashed = hash_password("secreto123")
    assert verificar_password("secreto123", hashed)
    assert not verificar_password("otra", hashed)


def test_mismo_password_distinto_hash():
    assert hash_password("abc") != hash_password("abc")


def test_formato_invalido_no_truena():
    assert not verificar_password("abc", "texto-plano")
