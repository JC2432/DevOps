from fastapi import APIRouter, HTTPException

from ..database import get_connection
from ..schemas import LoginIn
from ..seguridad import hash_password, verificar_password

router = APIRouter(tags=["auth"])

MENSAJE_ERROR = "Usuario o contraseña incorrectos"
# Hash de relleno: se verifica aunque el usuario no exista, para que la
# respuesta tarde igual y no se pueda averiguar qué usuarios existen.
_HASH_RELLENO = hash_password("relleno-no-valido")


@router.post("/login")
def login(datos: LoginIn):
    conn = get_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT u.USUARIO_ID AS id, u.USERNAME AS username, u.PASSWORD AS password,
                   u.NOMBRE AS nombre, u.APELLIDO_P AS apellido_p, c.PUESTO AS cargo
            FROM USUARIOS u JOIN CARGO c ON u.CARGO_ID = c.CARGO_ID
            WHERE u.USERNAME = %s
            """,
            (datos.username,),
        )
        usuario = cursor.fetchone()
    finally:
        conn.close()

    almacenado = usuario["password"] if usuario else _HASH_RELLENO
    password_ok = verificar_password(datos.password, almacenado)
    if not usuario or not password_ok:
        raise HTTPException(status_code=401, detail=MENSAJE_ERROR)
    if datos.cargo and datos.cargo.upper() != usuario["cargo"].upper():
        raise HTTPException(status_code=401, detail=MENSAJE_ERROR)

    usuario.pop("password")
    return usuario
