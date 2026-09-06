from fastapi import APIRouter, HTTPException
from ..database import get_connection

router = APIRouter(prefix="/usuarios", tags=["usuarios"])

# Nunca seleccionamos PASSWORD para no exponer credenciales en la API
CAMPOS_USUARIO = (
    "USUARIO_ID, CARGO_ID, USERNAME, NOMBRE, APELLIDO_P, APELLIDO_M"
)

@router.get("/")
def obtener_usuarios():
    """Devuelve la lista de usuarios, incluyendo el nombre del puesto legible."""
    conn = get_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT
                u.USUARIO_ID,
                u.CARGO_ID,
                c.PUESTO AS CARGO_NOMBRE,
                u.USERNAME,
                u.NOMBRE,
                u.APELLIDO_P,
                u.APELLIDO_M
            FROM USUARIOS u
            JOIN CARGO c ON u.CARGO_ID = c.CARGO_ID
            """
        )
        return {"usuarios": cursor.fetchall()}
    finally:
        conn.close()

@router.get("/{usuario_id}")
def obtener_usuario(usuario_id: str):
    """Devuelve un usuario específico por su id (USUARIO_ID, ej. 'U001')."""
    conn = get_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            f"SELECT {CAMPOS_USUARIO} FROM USUARIOS WHERE USUARIO_ID = %s",
            (usuario_id,),
        )
        resultado = cursor.fetchone()
        if not resultado:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        return resultado
    finally:
        conn.close()