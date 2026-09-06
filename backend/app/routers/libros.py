from fastapi import APIRouter, HTTPException
from ..database import get_connection, generar_siguiente_id
from ..schemas import LibroCreate, LibroUpdate

router = APIRouter(prefix="/libros", tags=["libros"])


@router.get("/")
def obtener_libros():
    """Devuelve la lista de libros registrados."""
    conn = get_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM LIBROS")
        return {"libros": cursor.fetchall()}
    finally:
        conn.close()


@router.get("/{libro_id}")
def obtener_libro(libro_id: str):
    """Devuelve un libro específico por su id."""
    conn = get_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM LIBROS WHERE LIBRO_ID = %s", (libro_id,))
        resultado = cursor.fetchone()
        if not resultado:
            raise HTTPException(status_code=404, detail="Libro no encontrado")
        return resultado
    finally:
        conn.close()


@router.post("/", status_code=201)
def crear_libro(libro: LibroCreate):
    """Registra un nuevo libro."""
    conn = get_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        nuevo_id = generar_siguiente_id(cursor, "LIBROS", "LIBRO_ID", "L", 3)
        cursor.execute(
            """
            INSERT INTO LIBROS (LIBRO_ID, EDITORIAL_ID, TITULO, ANIO_PUBLICACION, DISPONIBLE)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (
                nuevo_id,
                libro.EDITORIAL_ID,
                libro.TITULO,
                libro.ANIO_PUBLICACION,
                libro.DISPONIBLE,
            ),
        )
        conn.commit()
        return {"LIBRO_ID": nuevo_id, **libro.model_dump()}
    finally:
        conn.close()


@router.put("/{libro_id}")
def actualizar_disponibilidad(libro_id: str, datos: LibroUpdate):
    """Actualiza si un libro está disponible o no."""
    conn = get_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM LIBROS WHERE LIBRO_ID = %s", (libro_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Libro no encontrado")
        cursor.execute(
            "UPDATE LIBROS SET DISPONIBLE = %s WHERE LIBRO_ID = %s",
            (datos.DISPONIBLE, libro_id),
        )
        conn.commit()
        return {"LIBRO_ID": libro_id, "DISPONIBLE": datos.DISPONIBLE}
    finally:
        conn.close()