from fastapi import APIRouter, Depends, HTTPException

from ..dependencias import get_db, sesion_actual

router = APIRouter(prefix="/autores", tags=["autores"], dependencies=[Depends(sesion_actual)])

CONSULTA = """
    SELECT a.AUTOR_ID AS id,
           a.NOMBRE_AUTOR AS nombre,
           a.APELLIDO_P AS apellido_p,
           a.APELLIDO_M AS apellido_m,
           a.NACIONALIDAD_ID AS nacionalidad_id,
           n.NOMBRE AS nacionalidad
    FROM AUTORES a
    JOIN NACIONALIDAD n ON a.NACIONALIDAD_ID = n.NACIONALIDAD_ID
"""


@router.get("/")
def obtener_autores(conn=Depends(get_db)):
    """Devuelve la lista de autores, incluyendo su nacionalidad."""
    cursor = conn.cursor(dictionary=True)
    cursor.execute(f"{CONSULTA} ORDER BY a.AUTOR_ID")
    return cursor.fetchall()


@router.get("/{autor_id}")
def obtener_autor(autor_id: str, conn=Depends(get_db)):
    """Devuelve un autor específico por su id (ej. 'A001')."""
    cursor = conn.cursor(dictionary=True)
    cursor.execute(f"{CONSULTA} WHERE a.AUTOR_ID = %s", (autor_id,))
    resultado = cursor.fetchone()
    if not resultado:
        raise HTTPException(status_code=404, detail="Autor no encontrado")
    return resultado
