from backend.app.seguridad import crear_token, hash_password, leer_token, verificar_password


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


def test_token_valido():
    token = crear_token({"sub": "U001", "rol": "ADMINISTRADOR"})
    datos = leer_token(token)
    assert datos["sub"] == "U001" and datos["rol"] == "ADMINISTRADOR"


def test_token_alterado_no_es_valido():
    token = crear_token({"sub": "C001", "rol": "CLIENTE"})
    _, firma = token.split(".")
    # Intentar subir de rol cambiando los datos sin conocer la clave
    falso = crear_token({"sub": "C001", "rol": "ADMINISTRADOR"}).split(".")[0]
    assert leer_token(f"{falso}.{firma}") is None
    assert leer_token("basura") is None


def test_token_expirado_no_es_valido():
    assert leer_token(crear_token({"sub": "U001"}, horas=-1)) is None
