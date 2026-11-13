from fastapi import APIRouter, Depends, HTTPException

from ..database import actualizar_campos
from ..dependencias import get_db, solo_personal
from ..schemas import ClienteIn, ClienteUpdateIn
from ..seguridad import hash_password

# Solo el personal administra clientes. Los clientes ven sus datos en /mi.
router = APIRouter(prefix="/clientes", tags=["clientes"], dependencies=[Depends(solo_personal)])

# Nunca se devuelve PASSWORD; solo si el cliente tiene acceso al portal.
CONSULTA = """
    SELECT CLIENTE_ID AS id,
           NOMBRE AS nombre,
           APELLIDO_P AS apellido_p,
           APELLIDO_M AS apellido_m,
           CORREO AS correo,
           TELEFONO AS telefono,
           PASSWORD IS NOT NULL AS acceso_portal
    FROM CLIENTES
"""


def _formatear(fila):
    fila["acceso_portal"] = bool(fila["acceso_portal"])
    return fila


@router.get("/")
def obtener_clientes(conn=Depends(get_db)):
    cursor = conn.cursor(dictionary=True)
    cursor.execute(f"{CONSULTA} ORDER BY CLIENTE_ID")
    return [_formatear(f) for f in cursor.fetchall()]


@router.get("/{cliente_id}")
def obtener_cliente(cliente_id: str, conn=Depends(get_db)):
    cursor = conn.cursor(dictionary=True)
    cursor.execute(f"{CONSULTA} WHERE CLIENTE_ID = %s", (cliente_id,))
    resultado = cursor.fetchone()
    if not resultado:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    return _formatear(resultado)


@router.post("/", status_code=201)
def crear_cliente(cliente: ClienteIn, conn=Depends(get_db)):
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO CLIENTES
            (CLIENTE_ID, NOMBRE, APELLIDO_P, APELLIDO_M, CORREO, TELEFONO, PASSWORD)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """,
        (
            cliente.id, cliente.nombre, cliente.apellido_p, cliente.apellido_m or None,
            cliente.correo, cliente.telefono or None,
            hash_password(cliente.password) if cliente.password else None,
        ),
    )
    conn.commit()
    return {"id": cliente.id, "mensaje": "Cliente creado"}


@router.put("/{cliente_id}")
def actualizar_cliente(cliente_id: str, datos: ClienteUpdateIn, conn=Depends(get_db)):
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM CLIENTES WHERE CLIENTE_ID = %s", (cliente_id,))
    if not cursor.fetchone():
        raise HTTPException(status_code=404, detail="Cliente no encontrado")

    if datos.password:
        datos = datos.model_copy(update={"password": hash_password(datos.password)})
    mapeo = {
        "nombre": "NOMBRE", "apellido_p": "APELLIDO_P", "apellido_m": "APELLIDO_M",
        "correo": "CORREO", "telefono": "TELEFONO", "password": "PASSWORD",
    }
    if not actualizar_campos(cursor, "CLIENTES", "CLIENTE_ID", cliente_id, datos, mapeo):
        raise HTTPException(status_code=400, detail="No se enviaron campos para actualizar")
    conn.commit()
    return {"id": cliente_id, "mensaje": "Cliente actualizado"}


@router.delete("/{cliente_id}")
def eliminar_cliente(cliente_id: str, conn=Depends(get_db)):
    cursor = conn.cursor()
    # Si el cliente tiene préstamos, MySQL lo impide y la API responde 409.
    cursor.execute("DELETE FROM CLIENTES WHERE CLIENTE_ID = %s", (cliente_id,))
    if cursor.rowcount == 0:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    conn.commit()
    return {"mensaje": "Cliente eliminado"}
