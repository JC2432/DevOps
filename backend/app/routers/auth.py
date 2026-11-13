from fastapi import APIRouter, Depends, HTTPException

from ..dependencias import ROL_CLIENTE, get_db, sesion_actual
from ..schemas import LoginIn
from ..seguridad import crear_token, hash_password, verificar_password

router = APIRouter(tags=["auth"])

MENSAJE_ERROR = "Usuario o contraseña incorrectos"
# Hash de relleno: se verifica aunque el usuario no exista, para que la
# respuesta tarde igual y no se pueda averiguar qué usuarios existen.
_HASH_RELLENO = hash_password("relleno-no-valido")


def _buscar_personal(cursor, username):
    cursor.execute(
        """
        SELECT u.USUARIO_ID AS id, u.USERNAME AS username, u.PASSWORD AS password,
               u.NOMBRE AS nombre, u.APELLIDO_P AS apellido_p, c.PUESTO AS cargo
        FROM USUARIOS u JOIN CARGO c ON u.CARGO_ID = c.CARGO_ID
        WHERE u.USERNAME = %s
        """,
        (username,),
    )
    return cursor.fetchone()


def _buscar_cliente(cursor, correo):
    cursor.execute(
        """
        SELECT CLIENTE_ID AS id, CORREO AS username, PASSWORD AS password,
               NOMBRE AS nombre, APELLIDO_P AS apellido_p, 'CLIENTE' AS cargo
        FROM CLIENTES WHERE CORREO = %s
        """,
        (correo,),
    )
    return cursor.fetchone()


@router.post("/login")
def login(datos: LoginIn, conn=Depends(get_db)):
    """Inicia sesión y devuelve un token para mandar en `Authorization: Bearer <token>`.

    - Personal (BIBLIOTECARIO / ADMINISTRADOR): entra con su username.
    - Clientes (cargo = "CLIENTE"): entran con su correo.
    """
    cargo = (datos.cargo or "").upper()
    cursor = conn.cursor(dictionary=True)
    if cargo == ROL_CLIENTE:
        cuenta = _buscar_cliente(cursor, datos.username)
    else:
        cuenta = _buscar_personal(cursor, datos.username)

    # Un cliente sin contraseña (PASSWORD NULL) no tiene acceso al portal
    almacenado = cuenta["password"] if cuenta and cuenta["password"] else _HASH_RELLENO
    password_ok = verificar_password(datos.password, almacenado)
    if not cuenta or not cuenta["password"] or not password_ok:
        raise HTTPException(status_code=401, detail=MENSAJE_ERROR)
    if cargo and cargo != cuenta["cargo"].upper():
        raise HTTPException(status_code=401, detail=MENSAJE_ERROR)

    cuenta.pop("password")
    cuenta["rol"] = cuenta["cargo"]
    cuenta["token"] = crear_token(
        {"sub": cuenta["id"], "rol": cuenta["rol"], "nombre": cuenta["nombre"]}
    )
    return cuenta


@router.get("/sesion")
def ver_sesion(sesion: dict = Depends(sesion_actual)):
    """Devuelve quién es el dueño del token (útil para comprobar que sigue vigente)."""
    return {"id": sesion["sub"], "rol": sesion["rol"], "nombre": sesion["nombre"]}
