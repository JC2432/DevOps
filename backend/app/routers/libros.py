from fastapi import APIRouter, HTTPException
from ..database import get_connection

router = APIRouter(prefix="/libros", tags=["libros"])


@router.get("/")
def obtener_libros():
    """Devuelve la lista de libros registrados."""
    conn = get_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM LIBROS")
        resultados = cursor.fetchall()
        return {"libros": resultados}
    finally:
        conn.close()


@router.get("/{libro_id}")
def obtener_libro(libro_id: str):
    """Devuelve un libro específico por su id (LIBRO_ID, ej. 'L001')."""
    conn = get_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT * FROM LIBROS WHERE LIBRO_ID = %s", (libro_id,)
        )
        resultado = cursor.fetchone()
        if not resultado:
            raise HTTPException(status_code=404, detail="Libro no encontrado")
        return resultado
    finally:
        conn.close()