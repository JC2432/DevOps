"""Dependencias compartidas por los routers: conexión a la BD y control de acceso."""

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from .database import get_connection
from .seguridad import leer_token

ROL_CLIENTE = "CLIENTE"
ROLES_PERSONAL = {"BIBLIOTECARIO", "ADMINISTRADOR"}

_bearer = HTTPBearer(auto_error=False)


def get_db():
    """Conexión del pool para una petición.

    Si el endpoint lanza cualquier error se hace rollback, para que una operación a medias
    (p. ej. un préstamo con un libro no disponible) no deje datos sueltos.
    """
    conn = get_connection()
    try:
        yield conn
    except Exception:
        try:
            conn.rollback()
        except Exception:
            pass
        raise
    finally:
        conn.close()


def sesion_actual(
    credenciales: HTTPAuthorizationCredentials = Depends(_bearer),
) -> dict:
    if credenciales is None:
        raise HTTPException(
            status_code=401,
            detail="Inicia sesión para continuar",
            headers={"WWW-Authenticate": "Bearer"},
        )
    sesion = leer_token(credenciales.credentials)
    if sesion is None:
        raise HTTPException(
            status_code=401,
            detail="Tu sesión expiró. Vuelve a iniciar sesión",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return sesion


def solo_personal(sesion: dict = Depends(sesion_actual)) -> dict:
    if sesion.get("rol") not in ROLES_PERSONAL:
        raise HTTPException(
            status_code=403, detail="Solo el personal de la biblioteca puede hacer esto"
        )
    return sesion


def solo_cliente(sesion: dict = Depends(sesion_actual)) -> dict:
    if sesion.get("rol") != ROL_CLIENTE:
        raise HTTPException(status_code=403, detail="Esta sección es solo para clientes")
    return sesion
