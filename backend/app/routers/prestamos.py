from fastapi import APIRouter, HTTPException
from ..database import get_connection

router = APIRouter(prefix="/prestamos", tags=["prestamos"])


@router.get("/")
def obtener_prestamos():
    """Devuelve la lista de préstamos registrados."""
    conn = get_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM prestamos")
        resultados = cursor.fetchall()
        return {"prestamos": resultados}
    finally:
        conn.close()


@router.get("/{prestamo_id}")
def obtener_prestamo(prestamo_id: int):
    """Devuelve un préstamo específico por su id."""
    conn = get_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT * FROM prestamos WHERE id = %s", (prestamo_id,)
        )
        resultado = cursor.fetchone()
        if not resultado:
            raise HTTPException(status_code=404, detail="Préstamo no encontrado")
        return resultado
    finally:
        conn.close()
