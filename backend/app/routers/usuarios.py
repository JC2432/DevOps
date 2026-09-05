from fastapi import APIRouter, HTTPException
from ..database import get_connection

router = APIRouter(prefix="/usuarios", tags=["usuarios"])


@router.get("/")
def obtener_usuarios():
    """Devuelve la lista de usuarios registrados."""
    conn = get_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM usuarios")
        resultados = cursor.fetchall()
        return {"usuarios": resultados}
    finally:
        conn.close()


@router.get("/{usuario_id}")
def obtener_usuario(usuario_id: int):
    """Devuelve un usuario específico por su id."""
    conn = get_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM usuarios WHERE id = %s", (usuario_id,))
        resultado = cursor.fetchone()
        if not resultado:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        return resultado
    finally:
        conn.close()
