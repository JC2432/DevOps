"""Contraseñas y tokens de sesión (solo librería estándar, sin dependencias extra)."""

import base64
import hashlib
import hmac
import json
import os
import secrets
import time

ITERACIONES = 600_000
ALGORITMO = "pbkdf2_sha256"
DURACION_SESION_HORAS = 8

# Si no se define SECRET_KEY en el .env se usa una clave aleatoria: funciona, pero las
# sesiones se pierden cada vez que se reinicia el servidor.
_CLAVE_RESPALDO = secrets.token_hex(32)


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
    except (ValueError, AttributeError):
        return False
    if algoritmo != ALGORITMO:
        return False
    nuevo = hashlib.pbkdf2_hmac(
        "sha256", password.encode(), salt.encode(), int(iteraciones)
    ).hex()
    return hmac.compare_digest(nuevo, digest)


def _clave() -> bytes:
    return (os.getenv("SECRET_KEY") or _CLAVE_RESPALDO).encode()


def _firmar(cuerpo: str) -> str:
    return hmac.new(_clave(), cuerpo.encode(), hashlib.sha256).hexdigest()


def crear_token(datos: dict, horas: float = DURACION_SESION_HORAS) -> str:
    """Token firmado 'datos.firma'. Quien no conoce SECRET_KEY no puede falsificarlo."""
    payload = {**datos, "exp": int(time.time() + horas * 3600)}
    cuerpo = base64.urlsafe_b64encode(
        json.dumps(payload, separators=(",", ":")).encode()
    ).decode().rstrip("=")
    return f"{cuerpo}.{_firmar(cuerpo)}"


def leer_token(token: str):
    """Devuelve los datos del token, o None si fue alterado o ya expiró."""
    try:
        cuerpo, firma = token.split(".")
    except (ValueError, AttributeError):
        return None
    if not hmac.compare_digest(firma, _firmar(cuerpo)):
        return None
    try:
        relleno = "=" * (-len(cuerpo) % 4)
        payload = json.loads(base64.urlsafe_b64decode(cuerpo + relleno))
    except ValueError:
        return None
    if not isinstance(payload, dict) or payload.get("exp", 0) < time.time():
        return None
    return payload
