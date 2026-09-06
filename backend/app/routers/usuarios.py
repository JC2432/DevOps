from fastapi import APIRouter, HTTPException
from ..database import get_connection

router = APIRouter(prefix="/usuarios", tags=["usuarios"])

# Nunca seleccionamos PASSWORD para no exponer credenciales en la API
CAMPOS_USUARIO = (
    "USUARIO_ID, CARGO_ID, USERNAME, NOMBRE, APELLIDO_P, APELLIDO_M"
)


@router.get("/")
def obtener_usuarios():
    """Devuelve la lista de usuarios (bibliotecarios/administradores)."""
    conn = get_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(f"SELECT {CAMPOS_USUARIO} FROM USUARIOS")
        resultados = cursor.fetchall()
        return {"usuarios": resultados}
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