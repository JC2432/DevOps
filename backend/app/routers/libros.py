from fastapi import APIRouter, HTTPException
from ..database import get_connection

router = APIRouter(prefix="/libros", tags=["libros"])


@router.get("/")
def obtener_libros():
    """Devuelve la lista de libros registrados."""
    conn = get_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM libros")
        resultados = cursor.fetchall()
        return {"libros": resultados}
    finally:
        conn.close()


@router.get("/{libro_id}")
def obtener_libro(libro_id: int):
    """Devuelve un libro específico por su id."""
    conn = get_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM libros WHERE id = %s", (libro_id,))
        resultado = cursor.fetchone()
        if not resultado:
            raise HTTPException(status_code=404, detail="Libro no encontrado")
        return resultado
    finally:
        conn.close()
