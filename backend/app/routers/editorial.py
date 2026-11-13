from fastapi import APIRouter, Depends, HTTPException

from ..dependencias import get_db, sesion_actual

router = APIRouter(
    prefix="/editoriales", tags=["editoriales"], dependencies=[Depends(sesion_actual)]
)

CONSULTA = "SELECT EDITORIAL_ID AS id, NOMBRE AS nombre FROM EDITORIAL"


@router.get("/")
def obtener_editoriales(conn=Depends(get_db)):
    """Devuelve la lista de editoriales (también sirve para el selector de libros)."""
    cursor = conn.cursor(dictionary=True)
    cursor.execute(f"{CONSULTA} ORDER BY EDITORIAL_ID")
    return cursor.fetchall()


@router.get("/{editorial_id}")
def obtener_editorial(editorial_id: str, conn=Depends(get_db)):
    """Devuelve una editorial específica por su id (ej. 'E001')."""
    cursor = conn.cursor(dictionary=True)
    cursor.execute(f"{CONSULTA} WHERE EDITORIAL_ID = %s", (editorial_id,))
    resultado = cursor.fetchone()
    if not resultado:
        raise HTTPException(status_code=404, detail="Editorial no encontrada")
    return resultado
