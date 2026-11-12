"""Utilidades de contraseñas (solo librería estándar, sin dependencias extra)."""

import hashlib
import hmac
import secrets

ITERACIONES = 600_000
ALGORITMO = "pbkdf2_sha256"


def hash_password(password: str) -> str:
    """Devuelve 'algoritmo$iteraciones$salt$hash' (cabe en VARCHAR(255))."""
    salt = secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac(
        "sha256", password.encode(), salt.encode(), ITERACIONES
    ).hex()
    return f"{ALGORITMO}${ITERACIONES}${salt}${digest}"


def verificar_password(password: str, almacenado: str) -> bool:
    try:
        algoritmo, iteraciones, salt, digest = almacenado.split("$")
    except ValueError:
        return False
    if algoritmo != ALGORITMO:
        return False
    nuevo = hashlib.pbkdf2_hmac(
        "sha256", password.encode(), salt.encode(), int(iteraciones)
    ).hex()
    return hmac.compare_digest(nuevo, digest)
