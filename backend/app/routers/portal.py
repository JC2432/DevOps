"""Portal de clientes: cada cliente ve y aparta solo sus propios préstamos."""

from datetime import date, timedelta

from fastapi import APIRouter, Depends, HTTPException

from ..dependencias import get_db, solo_cliente
from ..schemas import ApartadoIn
from .prestamos import (
    ACTIVO, APARTADO, DIAS_PARA_RECOGER, VENCIDO,
    bloquear_prestamo, crear_prestamo, liberar_libros, listar_prestamos,
)

MAX_LIBROS_ABIERTOS = 5  # libros apartados + prestados que un cliente puede tener a la vez

router = APIRouter(prefix="/mi", tags=["portal de clientes"])


@router.get("/perfil")
def mi_perfil(sesion: dict = Depends(solo_cliente), conn=Depends(get_db)):
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        """
        SELECT CLIENTE_ID AS id, NOMBRE AS nombre, APELLIDO_P AS apellido_p,
               APELLIDO_M AS apellido_m, CORREO AS correo, TELEFONO AS telefono
        FROM CLIENTES WHERE CLIENTE_ID = %s
        """,
        (sesion["sub"],),
    )
    perfil = cursor.fetchone()
    if not perfil:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    return perfil


@router.get("/prestamos")
def mis_prestamos(sesion: dict = Depends(solo_cliente), conn=Depends(get_db)):
    return listar_prestamos(
        conn.cursor(dictionary=True), "WHERE p.CLIENTE_ID = %s", (sesion["sub"],)
    )


@router.post("/prestamos", status_code=201)
def apartar_libros(datos: ApartadoIn, sesion: dict = Depends(solo_cliente),
                   conn=Depends(get_db)):
    """Aparta libros para recogerlos en la biblioteca dentro de los próximos días."""
    cliente_id = sesion["sub"]
    cursor = conn.cursor(dictionary=True)

    cursor.execute(
        f"""
        SELECT COUNT(*) AS n FROM PRESTAMOS
        WHERE CLIENTE_ID = %s AND ESTADO_PRESTAMOS_ID IN ('{ACTIVO}', '{VENCIDO}')
          AND FECHA_DEVOLUCION IS NULL AND FECHA_LIMITE < CURDATE()
        """,
        (cliente_id,),
    )
    if cursor.fetchone()["n"]:
        raise HTTPException(
            status_code=409,
            detail="Tienes préstamos vencidos. Devuélvelos antes de apartar más libros.",
        )

    cursor.execute(
        """
        SELECT COUNT(*) AS n FROM LIBROS_PRESTADOS lp
        JOIN PRESTAMOS p ON p.PRESTAMO_ID = lp.PRESTAMO_ID
        WHERE p.CLIENTE_ID = %s AND p.FECHA_DEVOLUCION IS NULL
        """,
        (cliente_id,),
    )
    abiertos = cursor.fetchone()["n"]
    nuevos = len(set(datos.libros))
    if abiertos + nuevos > MAX_LIBROS_ABIERTOS:
        raise HTTPException(
            status_code=409,
            detail=f"Puedes tener hasta {MAX_LIBROS_ABIERTOS} libros a la vez "
                   f"(ya tienes {abiertos}).",
        )

    hoy = date.today()
    nuevo_id = crear_prestamo(
        cursor, cliente_id, datos.libros, APARTADO, None,
        hoy, hoy + timedelta(days=DIAS_PARA_RECOGER),
    )
    conn.commit()
    return {
        "id": nuevo_id,
        "mensaje": f"Libros apartados. Recógelos en la biblioteca en los próximos "
                   f"{DIAS_PARA_RECOGER} días.",
    }


@router.delete("/prestamos/{prestamo_id}")
def cancelar_apartado(prestamo_id: str, sesion: dict = Depends(solo_cliente),
                      conn=Depends(get_db)):
    """El cliente cancela un apartado que todavía no ha recogido."""
    cursor = conn.cursor(dictionary=True)
    prestamo = bloquear_prestamo(cursor, prestamo_id)
    # Mismo 404 si no existe o es de otro cliente: no revelamos préstamos ajenos
    if prestamo["CLIENTE_ID"] != sesion["sub"]:
        raise HTTPException(status_code=404, detail="Préstamo no encontrado")
    if prestamo["ESTADO_PRESTAMOS_ID"] != APARTADO:
        raise HTTPException(
            status_code=409, detail="Solo puedes cancelar apartados que no has recogido"
        )
    liberar_libros(cursor, prestamo_id)
    cursor.execute("DELETE FROM PRESTAMOS WHERE PRESTAMO_ID = %s", (prestamo_id,))
    conn.commit()
    return {"mensaje": "Apartado cancelado"}
