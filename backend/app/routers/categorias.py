from fastapi import APIRouter, HTTPException
from ..database import get_connection
from ..schemas import CategoriaIn, CategoriaUpdateIn

router = APIRouter(prefix="/categorias", tags=["categorias"])


@router.get("/")
def obtener_categorias():
    conn = get_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT CATEGORIA_ID AS id, NOMBRE_CATEGORIA AS nombre FROM CATEGORIAS")
        return cursor.fetchall()
    finally:
        conn.close()


@router.get("/{categoria_id}")
def obtener_categoria(categoria_id: str):
    conn = get_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT CATEGORIA_ID AS id, NOMBRE_CATEGORIA AS nombre FROM CATEGORIAS WHERE CATEGORIA_ID = %s",
            (categoria_id,),
        )
        resultado = cursor.fetchone()
        if not resultado:
            raise HTTPException(status_code=404, detail="Categoría no encontrada")
        return resultado
    finally:
        conn.close()


@router.post("/", status_code=201)
def crear_categoria(categoria: CategoriaIn):
    conn = get_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT CATEGORIA_ID FROM CATEGORIAS WHERE CATEGORIA_ID = %s", (categoria.id,))
        if cursor.fetchone():
            raise HTTPException(status_code=400, detail="Ya existe una categoría con ese ID")
        cursor.execute(
            "INSERT INTO CATEGORIAS (CATEGORIA_ID, NOMBRE_CATEGORIA) VALUES (%s, %s)",
            (categoria.id, categoria.nombre),
        )
        conn.commit()
        return {"id": categoria.id, "mensaje": "Categoría creada"}
    finally:
        conn.close()


@router.put("/{categoria_id}")
def actualizar_categoria(categoria_id: str, datos: CategoriaUpdateIn):
    conn = get_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM CATEGORIAS WHERE CATEGORIA_ID = %s", (categoria_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Categoría no encontrada")
        cursor.execute(
            "UPDATE CATEGORIAS SET NOMBRE_CATEGORIA = %s WHERE CATEGORIA_ID = %s",
            (datos.nombre, categoria_id),
        )
        conn.commit()
        return {"id": categoria_id, "mensaje": "Categoría actualizada"}
    finally:
        conn.close()


@router.delete("/{categoria_id}")
def eliminar_categoria(categoria_id: str):
    conn = get_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM CATEGORIAS WHERE CATEGORIA_ID = %s", (categoria_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Categoría no encontrada")
        try:
            cursor.execute("DELETE FROM CATEGORIAS WHERE CATEGORIA_ID = %s", (categoria_id,))
            conn.commit()
        except Exception:
            raise HTTPException(
                status_code=400,
                detail="No se pudo eliminar: la categoría está asignada a uno o más libros",
            )
        return {"mensaje": "Categoría eliminada"}
    finally:
        conn.close()