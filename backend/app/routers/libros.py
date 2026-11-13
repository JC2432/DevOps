from fastapi import APIRouter, Depends, HTTPException

from ..database import actualizar_campos
from ..dependencias import get_db, sesion_actual, solo_personal
from ..schemas import LibroIn, LibroUpdateIn

# Cualquier sesión (cliente o personal) puede consultar el catálogo;
# solo el personal puede modificarlo.
router = APIRouter(prefix="/libros", tags=["libros"], dependencies=[Depends(sesion_actual)])

CONSULTA_LIBROS = """
    SELECT l.LIBRO_ID AS id,
           l.EDITORIAL_ID AS editorial_id,
           e.NOMBRE AS editorial,
           l.TITULO AS titulo,
           l.ANIO_PUBLICACION AS anio,
           l.DISPONIBLE AS disponible,
           (SELECT GROUP_CONCAT(c.NOMBRE_CATEGORIA ORDER BY c.NOMBRE_CATEGORIA SEPARATOR ', ')
              FROM LIBROS_has_CATEGORIAS lc
              JOIN CATEGORIAS c ON c.CATEGORIA_ID = lc.CATEGORIA_ID
             WHERE lc.LIBRO_ID = l.LIBRO_ID) AS categorias
    FROM LIBROS l
    JOIN EDITORIAL e ON e.EDITORIAL_ID = l.EDITORIAL_ID
"""


def _como_bool(fila):
    # MySQL devuelve BOOLEAN como 0/1
    fila["disponible"] = bool(fila["disponible"])
    return fila


def _en_prestamo_abierto(cursor, libro_id):
    cursor.execute(
        """
        SELECT p.PRESTAMO_ID FROM LIBROS_PRESTADOS lp
        JOIN PRESTAMOS p ON p.PRESTAMO_ID = lp.PRESTAMO_ID
        WHERE lp.LIBRO_ID = %s AND p.FECHA_DEVOLUCION IS NULL
        LIMIT 1
        """,
        (libro_id,),
    )
    fila = cursor.fetchone()
    return fila["PRESTAMO_ID"] if fila else None


@router.get("/")
def obtener_libros(solo_disponibles: bool = False, conn=Depends(get_db)):
    cursor = conn.cursor(dictionary=True)
    filtro = " WHERE l.DISPONIBLE = TRUE" if solo_disponibles else ""
    cursor.execute(f"{CONSULTA_LIBROS}{filtro} ORDER BY l.LIBRO_ID")
    return [_como_bool(f) for f in cursor.fetchall()]


@router.get("/{libro_id}")
def obtener_libro(libro_id: str, conn=Depends(get_db)):
    cursor = conn.cursor(dictionary=True)
    cursor.execute(f"{CONSULTA_LIBROS} WHERE l.LIBRO_ID = %s", (libro_id,))
    resultado = cursor.fetchone()
    if not resultado:
        raise HTTPException(status_code=404, detail="Libro no encontrado")
    return _como_bool(resultado)


@router.post("/", status_code=201, dependencies=[Depends(solo_personal)])
def crear_libro(libro: LibroIn, conn=Depends(get_db)):
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        """
        INSERT INTO LIBROS (LIBRO_ID, EDITORIAL_ID, TITULO, ANIO_PUBLICACION, DISPONIBLE)
        VALUES (%s, %s, %s, %s, %s)
        """,
        (libro.id, libro.editorial_id, libro.titulo, libro.anio, libro.disponible),
    )
    conn.commit()
    return {"id": libro.id, "mensaje": "Libro creado"}


@router.put("/{libro_id}", dependencies=[Depends(solo_personal)])
def actualizar_libro(libro_id: str, datos: LibroUpdateIn, conn=Depends(get_db)):
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        "SELECT DISPONIBLE FROM LIBROS WHERE LIBRO_ID = %s FOR UPDATE", (libro_id,)
    )
    actual = cursor.fetchone()
    if not actual:
        raise HTTPException(status_code=404, detail="Libro no encontrado")

    # La disponibilidad la controlan los préstamos. A mano solo se puede cambiar
    # (p. ej. un ejemplar dañado o perdido) si el libro no está en un préstamo abierto.
    if datos.disponible is not None and datos.disponible != bool(actual["DISPONIBLE"]):
        prestamo = _en_prestamo_abierto(cursor, libro_id)
        if prestamo:
            raise HTTPException(
                status_code=409,
                detail=f"No se puede cambiar la disponibilidad: el libro está en el "
                       f"préstamo {prestamo}. Registra la devolución primero.",
            )

    mapeo = {
        "editorial_id": "EDITORIAL_ID",
        "titulo": "TITULO",
        "anio": "ANIO_PUBLICACION",
        "disponible": "DISPONIBLE",
    }
    if not actualizar_campos(cursor, "LIBROS", "LIBRO_ID", libro_id, datos, mapeo):
        raise HTTPException(status_code=400, detail="No se enviaron campos para actualizar")
    conn.commit()
    return {"id": libro_id, "mensaje": "Libro actualizado"}


@router.delete("/{libro_id}", dependencies=[Depends(solo_personal)])
def eliminar_libro(libro_id: str, conn=Depends(get_db)):
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT LIBRO_ID FROM LIBROS WHERE LIBRO_ID = %s", (libro_id,))
    if not cursor.fetchone():
        raise HTTPException(status_code=404, detail="Libro no encontrado")
    # Las relaciones con autores y categorías se quitan junto con el libro. Si aparece en
    # el historial de préstamos, MySQL lo impide y la API responde 409.
    cursor.execute("DELETE FROM AUTORES_has_LIBROS WHERE LIBRO_ID = %s", (libro_id,))
    cursor.execute("DELETE FROM LIBROS_has_CATEGORIAS WHERE LIBRO_ID = %s", (libro_id,))
    cursor.execute("DELETE FROM LIBROS WHERE LIBRO_ID = %s", (libro_id,))
    conn.commit()
    return {"mensaje": "Libro eliminado"}
