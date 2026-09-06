from fastapi import APIRouter, HTTPException
from ..database import get_connection, generar_siguiente_id
from ..schemas import PrestamoCreate

router = APIRouter(prefix="/prestamos", tags=["prestamos"])


@router.get("/")
def obtener_prestamos():
    """Devuelve la lista de préstamos registrados."""
    conn = get_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM PRESTAMOS")
        return {"prestamos": cursor.fetchall()}
    finally:
        conn.close()


@router.get("/{prestamo_id}")
def obtener_prestamo(prestamo_id: str):
    """Devuelve un préstamo específico, incluyendo los libros prestados."""
    conn = get_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM PRESTAMOS WHERE PRESTAMO_ID = %s", (prestamo_id,))
        prestamo = cursor.fetchone()
        if not prestamo:
            raise HTTPException(status_code=404, detail="Préstamo no encontrado")
        cursor.execute(
            "SELECT * FROM LIBROS_PRESTADOS WHERE PRESTAMO_ID = %s", (prestamo_id,)
        )
        prestamo["libros"] = cursor.fetchall()
        return prestamo
    finally:
        conn.close()


@router.post("/", status_code=201)
def crear_prestamo(prestamo: PrestamoCreate):
    """Registra un nuevo préstamo con uno o más libros."""
    conn = get_connection()
    try:
        cursor = conn.cursor(dictionary=True)

        # Validar que el cliente y el usuario existan
        cursor.execute(
            "SELECT * FROM CLIENTES WHERE CLIENTE_ID = %s", (prestamo.CLIENTE_ID,)
        )
        if not cursor.fetchone():
            raise HTTPException(status_code=400, detail="Cliente no existe")

        cursor.execute(
            "SELECT * FROM USUARIOS WHERE USUARIO_ID = %s", (prestamo.USUARIO_ID,)
        )
        if not cursor.fetchone():
            raise HTTPException(status_code=400, detail="Usuario no existe")

        nuevo_prestamo_id = generar_siguiente_id(
            cursor, "PRESTAMOS", "PRESTAMO_ID", "P", 3
        )

        # Estado inicial: ACTIVO (ajusta el ID si el de tu compañero es distinto)
        cursor.execute(
            """
            INSERT INTO PRESTAMOS
                (PRESTAMO_ID, ESTADO_PRESTAMOS_ID, CLIENTE_ID, USUARIO_ID, FECHA_PRESTAMO, FECHA_DEVOLUCION)
            VALUES (%s, 'S001', %s, %s, %s, NULL)
            """,
            (
                nuevo_prestamo_id,
                prestamo.CLIENTE_ID,
                prestamo.USUARIO_ID,
                prestamo.FECHA_PRESTAMO,
            ),
        )

        for item in prestamo.libros:
            cursor.execute(
                "SELECT DISPONIBLE FROM LIBROS WHERE LIBRO_ID = %s", (item.LIBRO_ID,)
            )
            libro = cursor.fetchone()
            if not libro:
                raise HTTPException(
                    status_code=400, detail=f"Libro {item.LIBRO_ID} no existe"
                )
            if not libro["DISPONIBLE"]:
                raise HTTPException(
                    status_code=400,
                    detail=f"Libro {item.LIBRO_ID} no está disponible",
                )

            nuevo_detalle_id = generar_siguiente_id(
                cursor, "LIBROS_PRESTADOS", "PRESTADOS_ID", "LP", 2
            )
            cursor.execute(
                """
                INSERT INTO LIBROS_PRESTADOS (PRESTADOS_ID, PRESTAMO_ID, LIBRO_ID, CANTIDAD)
                VALUES (%s, %s, %s, %s)
                """,
                (nuevo_detalle_id, nuevo_prestamo_id, item.LIBRO_ID, item.CANTIDAD),
            )
            cursor.execute(
                "UPDATE LIBROS SET DISPONIBLE = FALSE WHERE LIBRO_ID = %s",
                (item.LIBRO_ID,),
            )

        conn.commit()
        return {"PRESTAMO_ID": nuevo_prestamo_id, "mensaje": "Préstamo registrado"}
    finally:
        conn.close()


@router.put("/{prestamo_id}/devolver")
def registrar_devolucion(prestamo_id: str):
    """Marca un préstamo como devuelto y libera los libros."""
    conn = get_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM PRESTAMOS WHERE PRESTAMO_ID = %s", (prestamo_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Préstamo no encontrado")

        cursor.execute(
            """
            UPDATE PRESTAMOS
            SET ESTADO_PRESTAMOS_ID = 'S002', FECHA_DEVOLUCION = CURDATE()
            WHERE PRESTAMO_ID = %s
            """,
            (prestamo_id,),
        )

        cursor.execute(
            "SELECT LIBRO_ID FROM LIBROS_PRESTADOS WHERE PRESTAMO_ID = %s",
            (prestamo_id,),
        )
        libros = cursor.fetchall()
        for libro in libros:
            cursor.execute(
                "UPDATE LIBROS SET DISPONIBLE = TRUE WHERE LIBRO_ID = %s",
                (libro["LIBRO_ID"],),
            )

        conn.commit()
        return {"PRESTAMO_ID": prestamo_id, "mensaje": "Devolución registrada"}
    finally:
        conn.close()