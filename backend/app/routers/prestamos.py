from fastapi import APIRouter, HTTPException
from ..database import get_connection, generar_siguiente_id
from ..schemas import PrestamoIn, PrestamoUpdateIn

router = APIRouter(prefix="/prestamos", tags=["prestamos"])

CAMPOS_PRESTAMO = """
    p.PRESTAMO_ID AS id,
    p.ESTADO_PRESTAMOS_ID AS estado_id,
    ep.ESTADO AS estado,
    p.CLIENTE_ID AS cliente_id,
    CONCAT(c.NOMBRE, ' ', c.APELLIDO_P) AS cliente_nombre,
    p.USUARIO_ID AS usuario_id,
    p.FECHA_PRESTAMO AS fecha_prestamo,
    p.FECHA_DEVOLUCION AS fecha_devolucion
"""

JOIN_PRESTAMO = """
    FROM PRESTAMOS p
    JOIN CLIENTES c ON p.CLIENTE_ID = c.CLIENTE_ID
    JOIN ESTADO_PRESTAMOS ep ON p.ESTADO_PRESTAMOS_ID = ep.ESTADO_PRESTAMOS_ID
"""


@router.get("/")
def obtener_prestamos():
    conn = get_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(f"SELECT {CAMPOS_PRESTAMO} {JOIN_PRESTAMO} ORDER BY p.PRESTAMO_ID")
        return cursor.fetchall()
    finally:
        conn.close()


@router.get("/{prestamo_id}")
def obtener_prestamo(prestamo_id: str):
    conn = get_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(f"SELECT {CAMPOS_PRESTAMO} {JOIN_PRESTAMO} WHERE p.PRESTAMO_ID = %s", (prestamo_id,))
        prestamo = cursor.fetchone()
        if not prestamo:
            raise HTTPException(status_code=404, detail="Préstamo no encontrado")
        cursor.execute("SELECT * FROM LIBROS_PRESTADOS WHERE PRESTAMO_ID = %s", (prestamo_id,))
        prestamo["libros"] = cursor.fetchall()
        return prestamo
    finally:
        conn.close()


@router.post("/", status_code=201)
def crear_prestamo(prestamo: PrestamoIn):
    conn = get_connection()
    try:
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT * FROM CLIENTES WHERE CLIENTE_ID = %s", (prestamo.cliente_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=400, detail="Cliente no existe")
        cursor.execute("SELECT * FROM USUARIOS WHERE USUARIO_ID = %s", (prestamo.usuario_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=400, detail="Usuario no existe")
        cursor.execute(
            "SELECT * FROM ESTADO_PRESTAMOS WHERE ESTADO_PRESTAMOS_ID = %s",
            (prestamo.estado_prestamos_id,),
        )
        if not cursor.fetchone():
            raise HTTPException(status_code=400, detail="Estado de préstamo no existe")

        if prestamo.id:
            cursor.execute("SELECT PRESTAMO_ID FROM PRESTAMOS WHERE PRESTAMO_ID = %s", (prestamo.id,))
            if cursor.fetchone():
                raise HTTPException(status_code=400, detail="Ya existe un préstamo con ese ID")
            nuevo_id = prestamo.id
        else:
            nuevo_id = generar_siguiente_id(cursor, "PRESTAMOS", "PRESTAMO_ID", "P", 3)

        cursor.execute(
            """
            INSERT INTO PRESTAMOS
                (PRESTAMO_ID, ESTADO_PRESTAMOS_ID, CLIENTE_ID, USUARIO_ID, FECHA_PRESTAMO, FECHA_DEVOLUCION)
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (
                nuevo_id, prestamo.estado_prestamos_id, prestamo.cliente_id,
                prestamo.usuario_id, prestamo.fecha_prestamo, prestamo.fecha_devolucion,
            ),
        )

        if prestamo.libros:
            for item in prestamo.libros:
                cursor.execute("SELECT DISPONIBLE FROM LIBROS WHERE LIBRO_ID = %s", (item.LIBRO_ID,))
                libro = cursor.fetchone()
                if not libro:
                    raise HTTPException(status_code=400, detail=f"Libro {item.LIBRO_ID} no existe")
                if not libro["DISPONIBLE"]:
                    raise HTTPException(status_code=400, detail=f"Libro {item.LIBRO_ID} no está disponible")
                nuevo_detalle_id = generar_siguiente_id(cursor, "LIBROS_PRESTADOS", "PRESTADOS_ID", "LP", 2)
                cursor.execute(
                    """
                    INSERT INTO LIBROS_PRESTADOS (PRESTADOS_ID, PRESTAMO_ID, LIBRO_ID, CANTIDAD)
                    VALUES (%s, %s, %s, %s)
                    """,
                    (nuevo_detalle_id, nuevo_id, item.LIBRO_ID, item.CANTIDAD),
                )
                cursor.execute("UPDATE LIBROS SET DISPONIBLE = FALSE WHERE LIBRO_ID = %s", (item.LIBRO_ID,))

        conn.commit()
        return {"id": nuevo_id, "mensaje": "Préstamo registrado"}
    finally:
        conn.close()


@router.put("/{prestamo_id}")
def actualizar_prestamo(prestamo_id: str, datos: PrestamoUpdateIn):
    conn = get_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM PRESTAMOS WHERE PRESTAMO_ID = %s", (prestamo_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Préstamo no encontrado")

        mapeo = {
            "estado_prestamos_id": "ESTADO_PRESTAMOS_ID", "cliente_id": "CLIENTE_ID",
            "usuario_id": "USUARIO_ID", "fecha_prestamo": "FECHA_PRESTAMO",
            "fecha_devolucion": "FECHA_DEVOLUCION",
        }
        campos, valores = [], []
        for campo_py, campo_sql in mapeo.items():
            valor = getattr(datos, campo_py)
            if valor is not None:
                campos.append(f"{campo_sql} = %s")
                valores.append(valor)
        if not campos:
            raise HTTPException(status_code=400, detail="No se enviaron campos para actualizar")
        valores.append(prestamo_id)
        cursor.execute(f"UPDATE PRESTAMOS SET {', '.join(campos)} WHERE PRESTAMO_ID = %s", tuple(valores))
        conn.commit()
        return {"id": prestamo_id, "mensaje": "Préstamo actualizado"}
    finally:
        conn.close()


@router.put("/{prestamo_id}/devolver")
def registrar_devolucion(prestamo_id: str):
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
        cursor.execute("SELECT LIBRO_ID FROM LIBROS_PRESTADOS WHERE PRESTAMO_ID = %s", (prestamo_id,))
        for libro in cursor.fetchall():
            cursor.execute("UPDATE LIBROS SET DISPONIBLE = TRUE WHERE LIBRO_ID = %s", (libro["LIBRO_ID"],))
        conn.commit()
        return {"id": prestamo_id, "mensaje": "Devolución registrada"}
    finally:
        conn.close()


@router.delete("/{prestamo_id}")
def eliminar_prestamo(prestamo_id: str):
    conn = get_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM PRESTAMOS WHERE PRESTAMO_ID = %s", (prestamo_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Préstamo no encontrado")
        cursor.execute("SELECT LIBRO_ID FROM LIBROS_PRESTADOS WHERE PRESTAMO_ID = %s", (prestamo_id,))
        libros_asociados = cursor.fetchall()
        cursor.execute("DELETE FROM LIBROS_PRESTADOS WHERE PRESTAMO_ID = %s", (prestamo_id,))
        for libro in libros_asociados:
            cursor.execute("UPDATE LIBROS SET DISPONIBLE = TRUE WHERE LIBRO_ID = %s", (libro["LIBRO_ID"],))
        cursor.execute("DELETE FROM PRESTAMOS WHERE PRESTAMO_ID = %s", (prestamo_id,))
        conn.commit()
        return {"mensaje": "Préstamo eliminado"}
    finally:
        conn.close()