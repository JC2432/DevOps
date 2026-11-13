"""Préstamos (vista del personal) y la lógica compartida con el portal de clientes.

Ciclo de vida de un préstamo:

    cliente aparta en el portal ──> APARTADO ──(personal: entregar)──> ACTIVO
    personal presta en mostrador ─────────────────────────────────────> ACTIVO
    ACTIVO ──(personal: devolver)──> DEVUELTO

Un préstamo ACTIVO cuya fecha límite ya pasó se muestra como VENCIDO.
Mientras el préstamo está abierto (APARTADO o ACTIVO) sus libros quedan no disponibles.
"""

from datetime import date, timedelta

from fastapi import APIRouter, Depends, HTTPException

from ..database import generar_siguiente_id
from ..dependencias import get_db, solo_personal
from ..schemas import PrestamoIn, PrestamoUpdateIn

ACTIVO = "S001"
DEVUELTO = "S002"
VENCIDO = "S003"  # solo por compatibilidad con datos viejos; se calcula con la fecha
APARTADO = "S004"

DIAS_PRESTAMO = 14      # duración de un préstamo desde que se entrega
DIAS_PARA_RECOGER = 3   # plazo para recoger un apartado

CAMPOS = f"""
    p.PRESTAMO_ID AS id,
    p.ESTADO_PRESTAMOS_ID AS estado_id,
    CASE WHEN p.ESTADO_PRESTAMOS_ID IN ('{ACTIVO}', '{VENCIDO}')
              AND p.FECHA_LIMITE < CURDATE() THEN 'VENCIDO'
         WHEN p.ESTADO_PRESTAMOS_ID = '{VENCIDO}' THEN 'ACTIVO'
         ELSE ep.ESTADO END AS estado,
    p.CLIENTE_ID AS cliente_id,
    CONCAT(c.NOMBRE, ' ', c.APELLIDO_P) AS cliente_nombre,
    p.USUARIO_ID AS usuario_id,
    p.FECHA_PRESTAMO AS fecha_prestamo,
    p.FECHA_LIMITE AS fecha_limite,
    p.FECHA_DEVOLUCION AS fecha_devolucion,
    CASE WHEN p.FECHA_DEVOLUCION IS NULL
         THEN DATEDIFF(p.FECHA_LIMITE, CURDATE()) END AS dias_restantes
"""

JOINS = """
    FROM PRESTAMOS p
    JOIN CLIENTES c ON p.CLIENTE_ID = c.CLIENTE_ID
    JOIN ESTADO_PRESTAMOS ep ON p.ESTADO_PRESTAMOS_ID = ep.ESTADO_PRESTAMOS_ID
"""

router = APIRouter(prefix="/prestamos", tags=["prestamos"], dependencies=[Depends(solo_personal)])


# ---------------------------------------------------------------------------
# Lógica compartida (también la usa el portal de clientes en portal.py)
# ---------------------------------------------------------------------------

def listar_prestamos(cursor, where="", params=()):
    """Préstamos con la lista de libros de cada uno, del más reciente al más antiguo."""
    cursor.execute(
        f"SELECT {CAMPOS} {JOINS} {where} "
        f"ORDER BY CAST(SUBSTRING(p.PRESTAMO_ID, 2) AS UNSIGNED) DESC",
        params,
    )
    prestamos = cursor.fetchall()
    if not prestamos:
        return []

    por_id = {p["id"]: p for p in prestamos}
    for p in prestamos:
        p["libros"] = []
    marcas = ", ".join(["%s"] * len(por_id))
    cursor.execute(
        f"""
        SELECT lp.PRESTAMO_ID AS prestamo_id, l.LIBRO_ID AS id, l.TITULO AS titulo
        FROM LIBROS_PRESTADOS lp JOIN LIBROS l ON l.LIBRO_ID = lp.LIBRO_ID
        WHERE lp.PRESTAMO_ID IN ({marcas})
        ORDER BY l.TITULO
        """,
        tuple(por_id),
    )
    for fila in cursor.fetchall():
        por_id[fila.pop("prestamo_id")]["libros"].append(fila)
    return prestamos


def obtener_uno(cursor, prestamo_id):
    resultado = listar_prestamos(cursor, "WHERE p.PRESTAMO_ID = %s", (prestamo_id,))
    if not resultado:
        raise HTTPException(status_code=404, detail="Préstamo no encontrado")
    return resultado[0]


def bloquear_prestamo(cursor, prestamo_id):
    """Lee el préstamo con FOR UPDATE para cambiarlo sin que otra petición lo toque."""
    cursor.execute(
        "SELECT * FROM PRESTAMOS WHERE PRESTAMO_ID = %s FOR UPDATE", (prestamo_id,)
    )
    prestamo = cursor.fetchone()
    if not prestamo:
        raise HTTPException(status_code=404, detail="Préstamo no encontrado")
    return prestamo


def crear_prestamo(cursor, cliente_id, libros, estado, usuario_id, fecha_prestamo, fecha_limite):
    """Registra un préstamo y marca sus libros como no disponibles. Devuelve el nuevo ID."""
    cursor.execute("SELECT 1 FROM CLIENTES WHERE CLIENTE_ID = %s", (cliente_id,))
    if not cursor.fetchone():
        raise HTTPException(status_code=400, detail=f"El cliente {cliente_id} no existe")

    libros = list(dict.fromkeys(libros))  # quita repetidos conservando el orden
    marcas = ", ".join(["%s"] * len(libros))
    # FOR UPDATE: si dos personas apartan el mismo libro al mismo tiempo, la segunda espera
    # a que termine la primera y entonces ya lo ve como no disponible.
    cursor.execute(
        f"SELECT LIBRO_ID, TITULO, DISPONIBLE FROM LIBROS WHERE LIBRO_ID IN ({marcas}) "
        f"FOR UPDATE",
        tuple(libros),
    )
    encontrados = {f["LIBRO_ID"]: f for f in cursor.fetchall()}
    faltantes = [lid for lid in libros if lid not in encontrados]
    if faltantes:
        raise HTTPException(
            status_code=400, detail=f"Estos libros no existen: {', '.join(faltantes)}"
        )
    ocupados = [encontrados[lid]["TITULO"] for lid in libros if not encontrados[lid]["DISPONIBLE"]]
    if ocupados:
        raise HTTPException(
            status_code=409, detail=f"Estos libros ya no están disponibles: {', '.join(ocupados)}"
        )

    nuevo_id = generar_siguiente_id(cursor, "PRESTAMOS", "PRESTAMO_ID", "P", 3)
    cursor.execute(
        """
        INSERT INTO PRESTAMOS
            (PRESTAMO_ID, ESTADO_PRESTAMOS_ID, CLIENTE_ID, USUARIO_ID,
             FECHA_PRESTAMO, FECHA_LIMITE)
        VALUES (%s, %s, %s, %s, %s, %s)
        """,
        (nuevo_id, estado, cliente_id, usuario_id, fecha_prestamo, fecha_limite),
    )
    cursor.executemany(
        "INSERT INTO LIBROS_PRESTADOS (PRESTAMO_ID, LIBRO_ID) VALUES (%s, %s)",
        [(nuevo_id, lid) for lid in libros],
    )
    cursor.execute(
        f"UPDATE LIBROS SET DISPONIBLE = FALSE WHERE LIBRO_ID IN ({marcas})", tuple(libros)
    )
    return nuevo_id


def liberar_libros(cursor, prestamo_id):
    """Vuelve a poner disponibles los libros de un préstamo.

    Solo se debe llamar para préstamos abiertos (sin FECHA_DEVOLUCION): un libro solo
    puede estar en un préstamo abierto a la vez, así que no se libera por error un libro
    que ya se prestó a otra persona.
    """
    cursor.execute(
        """
        UPDATE LIBROS l JOIN LIBROS_PRESTADOS lp ON lp.LIBRO_ID = l.LIBRO_ID
        SET l.DISPONIBLE = TRUE
        WHERE lp.PRESTAMO_ID = %s
        """,
        (prestamo_id,),
    )


# ---------------------------------------------------------------------------
# Endpoints del personal
# ---------------------------------------------------------------------------

@router.get("/")
def obtener_prestamos(conn=Depends(get_db)):
    return listar_prestamos(conn.cursor(dictionary=True))


@router.get("/{prestamo_id}")
def obtener_prestamo(prestamo_id: str, conn=Depends(get_db)):
    return obtener_uno(conn.cursor(dictionary=True), prestamo_id)


@router.post("/", status_code=201)
def registrar_prestamo(datos: PrestamoIn, sesion: dict = Depends(solo_personal),
                       conn=Depends(get_db)):
    """Préstamo en mostrador: el cliente se lleva los libros en este momento."""
    fecha_prestamo = datos.fecha_prestamo or date.today()
    fecha_limite = datos.fecha_limite or fecha_prestamo + timedelta(days=DIAS_PRESTAMO)
    if fecha_limite < fecha_prestamo:
        raise HTTPException(
            status_code=400, detail="La fecha límite no puede ser anterior a la del préstamo"
        )
    cursor = conn.cursor(dictionary=True)
    nuevo_id = crear_prestamo(
        cursor, datos.cliente_id, datos.libros, ACTIVO, sesion["sub"],
        fecha_prestamo, fecha_limite,
    )
    conn.commit()
    return {"id": nuevo_id, "mensaje": "Préstamo registrado"}


@router.put("/{prestamo_id}")
def actualizar_prestamo(prestamo_id: str, datos: PrestamoUpdateIn, conn=Depends(get_db)):
    """Corrige fechas o renueva el préstamo (amplía la fecha límite)."""
    cursor = conn.cursor(dictionary=True)
    actual = bloquear_prestamo(cursor, prestamo_id)
    if actual["FECHA_DEVOLUCION"] is not None:
        raise HTTPException(status_code=409, detail="El préstamo ya fue devuelto")
    if datos.fecha_prestamo is None and datos.fecha_limite is None:
        raise HTTPException(status_code=400, detail="No se enviaron campos para actualizar")

    fecha_prestamo = datos.fecha_prestamo or actual["FECHA_PRESTAMO"]
    fecha_limite = datos.fecha_limite or actual["FECHA_LIMITE"]
    if fecha_limite < fecha_prestamo:
        raise HTTPException(
            status_code=400, detail="La fecha límite no puede ser anterior a la del préstamo"
        )
    cursor.execute(
        "UPDATE PRESTAMOS SET FECHA_PRESTAMO = %s, FECHA_LIMITE = %s WHERE PRESTAMO_ID = %s",
        (fecha_prestamo, fecha_limite, prestamo_id),
    )
    conn.commit()
    return {"id": prestamo_id, "mensaje": "Préstamo actualizado"}


@router.put("/{prestamo_id}/entregar")
def entregar_apartado(prestamo_id: str, sesion: dict = Depends(solo_personal),
                      conn=Depends(get_db)):
    """El cliente pasó a recoger su apartado: el préstamo empieza a contar desde hoy."""
    cursor = conn.cursor(dictionary=True)
    actual = bloquear_prestamo(cursor, prestamo_id)
    if actual["ESTADO_PRESTAMOS_ID"] != APARTADO:
        raise HTTPException(status_code=409, detail="Solo se pueden entregar préstamos apartados")
    cursor.execute(
        """
        UPDATE PRESTAMOS
        SET ESTADO_PRESTAMOS_ID = %s, USUARIO_ID = %s, FECHA_PRESTAMO = CURDATE(),
            FECHA_LIMITE = CURDATE() + INTERVAL %s DAY
        WHERE PRESTAMO_ID = %s
        """,
        (ACTIVO, sesion["sub"], DIAS_PRESTAMO, prestamo_id),
    )
    conn.commit()
    return {"id": prestamo_id, "mensaje": "Libros entregados al cliente"}


@router.put("/{prestamo_id}/devolver")
def registrar_devolucion(prestamo_id: str, conn=Depends(get_db)):
    cursor = conn.cursor(dictionary=True)
    actual = bloquear_prestamo(cursor, prestamo_id)
    if actual["FECHA_DEVOLUCION"] is not None:
        raise HTTPException(status_code=409, detail="Este préstamo ya fue devuelto")
    if actual["ESTADO_PRESTAMOS_ID"] == APARTADO:
        raise HTTPException(
            status_code=409,
            detail="Este préstamo está apartado y nunca se entregó: entrégalo o elimínalo",
        )
    cursor.execute(
        """
        UPDATE PRESTAMOS SET ESTADO_PRESTAMOS_ID = %s, FECHA_DEVOLUCION = CURDATE()
        WHERE PRESTAMO_ID = %s
        """,
        (DEVUELTO, prestamo_id),
    )
    liberar_libros(cursor, prestamo_id)
    conn.commit()
    return {"id": prestamo_id, "mensaje": "Devolución registrada"}


@router.delete("/{prestamo_id}")
def eliminar_prestamo(prestamo_id: str, conn=Depends(get_db)):
    cursor = conn.cursor(dictionary=True)
    actual = bloquear_prestamo(cursor, prestamo_id)
    # Si ya se devolvió, sus libros pueden estar prestados a otra persona: no se tocan.
    if actual["FECHA_DEVOLUCION"] is None:
        liberar_libros(cursor, prestamo_id)
    # El detalle (LIBROS_PRESTADOS) se borra en cascada
    cursor.execute("DELETE FROM PRESTAMOS WHERE PRESTAMO_ID = %s", (prestamo_id,))
    conn.commit()
    return {"mensaje": "Préstamo eliminado"}
