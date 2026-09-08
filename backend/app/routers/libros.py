from fastapi import APIRouter, HTTPException
from ..database import get_connection
from ..schemas import LibroIn, LibroUpdateIn

router = APIRouter(prefix="/libros", tags=["libros"])

CAMPOS_LIBRO = """
    LIBRO_ID AS id,
    EDITORIAL_ID AS editorial_id,
    TITULO AS titulo,
    ANIO_PUBLICACION AS anio,
    DISPONIBLE AS disponible
"""


@router.get("/")
def obtener_libros():
    conn = get_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(f"SELECT {CAMPOS_LIBRO} FROM LIBROS")
        return cursor.fetchall()
    finally:
        conn.close()


@router.get("/{libro_id}")
def obtener_libro(libro_id: str):
    conn = get_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(f"SELECT {CAMPOS_LIBRO} FROM LIBROS WHERE LIBRO_ID = %s", (libro_id,))
        resultado = cursor.fetchone()
        if not resultado:
            raise HTTPException(status_code=404, detail="Libro no encontrado")
        return resultado
    finally:
        conn.close()


@router.post("/", status_code=201)
def crear_libro(libro: LibroIn):
    conn = get_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT LIBRO_ID FROM LIBROS WHERE LIBRO_ID = %s", (libro.id,))
        if cursor.fetchone():
            raise HTTPException(status_code=400, detail="Ya existe un libro con ese ID")
        cursor.execute(
            """
            INSERT INTO LIBROS (LIBRO_ID, EDITORIAL_ID, TITULO, ANIO_PUBLICACION, DISPONIBLE)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (libro.id, libro.editorial_id, libro.titulo, libro.anio, libro.disponible),
        )
        conn.commit()
        return {"id": libro.id, "mensaje": "Libro creado"}
    finally:
        conn.close()


@router.put("/{libro_id}")
def actualizar_libro(libro_id: str, datos: LibroUpdateIn):
    conn = get_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM LIBROS WHERE LIBRO_ID = %s", (libro_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Libro no encontrado")

        mapeo = {
            "editorial_id": "EDITORIAL_ID",
            "titulo": "TITULO",
            "anio": "ANIO_PUBLICACION",
            "disponible": "DISPONIBLE",
        }
        campos, valores = [], []
        for campo_py, campo_sql in mapeo.items():
            valor = getattr(datos, campo_py)
            if valor is not None:
                campos.append(f"{campo_sql} = %s")
                valores.append(valor)
        if not campos:
            raise HTTPException(status_code=400, detail="No se enviaron campos para actualizar")
        valores.append(libro_id)
        cursor.execute(f"UPDATE LIBROS SET {', '.join(campos)} WHERE LIBRO_ID = %s", tuple(valores))
        conn.commit()
        return {"id": libro_id, "mensaje": "Libro actualizado"}
    finally:
        conn.close()


@router.delete("/{libro_id}")
def eliminar_libro(libro_id: str):
    conn = get_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM LIBROS WHERE LIBRO_ID = %s", (libro_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Libro no encontrado")
        try:
            cursor.execute("DELETE FROM LIBROS WHERE LIBRO_ID = %s", (libro_id,))
            conn.commit()
        except Exception:
            raise HTTPException(
                status_code=400,
                detail="No se pudo eliminar: el libro está asignado a un préstamo o categoría",
            )
        return {"mensaje": "Libro eliminado"}
    finally:
        conn.close()