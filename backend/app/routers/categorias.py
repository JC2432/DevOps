from fastapi import APIRouter, HTTPException
from ..database import get_connection

router = APIRouter(prefix="/categorias", tags=["categorias"])

@router.get("/")
def obtener_categorias():
    """Devuelve la lista de categorías."""
    conn = get_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM CATEGORIAS")
        resultados = cursor.fetchall()
        return {"categorias": resultados}
    finally:
        conn.close()

@router.get("/{categoria_id}")
def obtener_categoria(categoria_id: str):
    """Devuelve una categoría específica por su id (CATEGORIA_ID, ej. 'CAT001')."""
    conn = get_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT * FROM CATEGORIAS WHERE CATEGORIA_ID = %s",
            (categoria_id,),
        )
        resultado = cursor.fetchone()
        if not resultado:
            raise HTTPException(status_code=404, detail="Categoría no encontrada")
        return resultado
    finally:
        conn.close()

        