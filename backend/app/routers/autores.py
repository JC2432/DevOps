from fastapi import APIRouter, HTTPException
from ..database import get_connection

router = APIRouter(prefix="/autores", tags=["autores"])


@router.get("/")
def obtener_autores():
    """Devuelve la lista de autores, incluyendo su nacionalidad."""
    conn = get_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT a.*, n.NOMBRE AS NACIONALIDAD
            FROM AUTORES a
            JOIN NACIONALIDAD n ON a.NACIONALIDAD_ID = n.NACIONALIDAD_ID
            """
        )
        resultados = cursor.fetchall()
        return {"autores": resultados}
    finally:
        conn.close()


@router.get("/{autor_id}")
def obtener_autor(autor_id: str):
    """Devuelve un autor específico por su id (AUTOR_ID, ej. 'A001')."""
    conn = get_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT a.*, n.NOMBRE AS NACIONALIDAD
            FROM AUTORES a
            JOIN NACIONALIDAD n ON a.NACIONALIDAD_ID = n.NACIONALIDAD_ID
            WHERE a.AUTOR_ID = %s
            """,
            (autor_id,),
        )
        resultado = cursor.fetchone()
        if not resultado:
            raise HTTPException(status_code=404, detail="Autor no encontrado")
        return resultado
    finally:
        conn.close()