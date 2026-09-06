from fastapi import APIRouter, HTTPException
from ..database import get_connection

router = APIRouter(prefix="/editoriales", tags=["editoriales"])


@router.get("/")
def obtener_editoriales():
    """Devuelve la lista de editoriales."""
    conn = get_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM EDITORIALES")
        resultados = cursor.fetchall()
        return {"editoriales": resultados}
    finally:
        conn.close()

@router.get("/{editorial_id}")
def obtener_editorial(editorial_id: str):
    """Devuelve una editorial específica por su id (EDITORIAL_ID, ej. 'E001')."""
    conn = get_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT * FROM EDITORIALES WHERE EDITORIAL_ID = %s",
            (editorial_id,),
        )
        resultado = cursor.fetchone()
        if not resultado:
            raise HTTPException(status_code=404, detail="Editorial no encontrada")
        return resultado
    finally:
        conn.close()