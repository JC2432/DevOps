from fastapi import APIRouter, Depends, HTTPException

from ..dependencias import get_db, sesion_actual, solo_personal
from ..schemas import CategoriaIn, CategoriaUpdateIn

router = APIRouter(
    prefix="/categorias", tags=["categorias"], dependencies=[Depends(sesion_actual)]
)

CONSULTA = "SELECT CATEGORIA_ID AS id, NOMBRE_CATEGORIA AS nombre FROM CATEGORIAS"


@router.get("/")
def obtener_categorias(conn=Depends(get_db)):
    cursor = conn.cursor(dictionary=True)
    cursor.execute(f"{CONSULTA} ORDER BY CATEGORIA_ID")
    return cursor.fetchall()


@router.get("/{categoria_id}")
def obtener_categoria(categoria_id: str, conn=Depends(get_db)):
    cursor = conn.cursor(dictionary=True)
    cursor.execute(f"{CONSULTA} WHERE CATEGORIA_ID = %s", (categoria_id,))
    resultado = cursor.fetchone()
    if not resultado:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")
    return resultado


@router.post("/", status_code=201, dependencies=[Depends(solo_personal)])
def crear_categoria(categoria: CategoriaIn, conn=Depends(get_db)):
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO CATEGORIAS (CATEGORIA_ID, NOMBRE_CATEGORIA) VALUES (%s, %s)",
        (categoria.id, categoria.nombre),
    )
    conn.commit()
    return {"id": categoria.id, "mensaje": "Categoría creada"}


@router.put("/{categoria_id}", dependencies=[Depends(solo_personal)])
def actualizar_categoria(categoria_id: str, datos: CategoriaUpdateIn, conn=Depends(get_db)):
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE CATEGORIAS SET NOMBRE_CATEGORIA = %s WHERE CATEGORIA_ID = %s",
        (datos.nombre, categoria_id),
    )
    cursor.execute("SELECT 1 FROM CATEGORIAS WHERE CATEGORIA_ID = %s", (categoria_id,))
    if not cursor.fetchone():
        raise HTTPException(status_code=404, detail="Categoría no encontrada")
    conn.commit()
    return {"id": categoria_id, "mensaje": "Categoría actualizada"}


@router.delete("/{categoria_id}", dependencies=[Depends(solo_personal)])
def eliminar_categoria(categoria_id: str, conn=Depends(get_db)):
    cursor = conn.cursor()
    # Si la categoría está asignada a libros, MySQL lo impide y la API responde 409.
    cursor.execute("DELETE FROM CATEGORIAS WHERE CATEGORIA_ID = %s", (categoria_id,))
    if cursor.rowcount == 0:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")
    conn.commit()
    return {"mensaje": "Categoría eliminada"}
