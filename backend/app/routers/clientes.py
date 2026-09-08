from fastapi import APIRouter, HTTPException
from ..database import get_connection
from ..schemas import ClienteIn, ClienteUpdateIn

router = APIRouter(prefix="/clientes", tags=["clientes"])

CAMPOS_CLIENTE = """
    CLIENTE_ID AS id,
    NOMBRE AS nombre,
    APELLIDO_P AS apellido_p,
    APELLIDO_M AS apellido_m,
    CORREO AS correo,
    TELEFONO AS telefono
"""


@router.get("/")
def obtener_clientes():
    conn = get_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(f"SELECT {CAMPOS_CLIENTE} FROM CLIENTES")
        return cursor.fetchall()
    finally:
        conn.close()


@router.get("/{cliente_id}")
def obtener_cliente(cliente_id: str):
    conn = get_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(f"SELECT {CAMPOS_CLIENTE} FROM CLIENTES WHERE CLIENTE_ID = %s", (cliente_id,))
        resultado = cursor.fetchone()
        if not resultado:
            raise HTTPException(status_code=404, detail="Cliente no encontrado")
        return resultado
    finally:
        conn.close()


@router.post("/", status_code=201)
def crear_cliente(cliente: ClienteIn):
    conn = get_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT CLIENTE_ID FROM CLIENTES WHERE CLIENTE_ID = %s", (cliente.id,))
        if cursor.fetchone():
            raise HTTPException(status_code=400, detail="Ya existe un cliente con ese ID")
        cursor.execute(
            """
            INSERT INTO CLIENTES (CLIENTE_ID, NOMBRE, APELLIDO_P, APELLIDO_M, CORREO, TELEFONO)
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (cliente.id, cliente.nombre, cliente.apellido_p, cliente.apellido_m, cliente.correo, cliente.telefono),
        )
        conn.commit()
        return {"id": cliente.id, "mensaje": "Cliente creado"}
    finally:
        conn.close()


@router.put("/{cliente_id}")
def actualizar_cliente(cliente_id: str, datos: ClienteUpdateIn):
    conn = get_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM CLIENTES WHERE CLIENTE_ID = %s", (cliente_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Cliente no encontrado")

        mapeo = {
            "nombre": "NOMBRE", "apellido_p": "APELLIDO_P", "apellido_m": "APELLIDO_M",
            "correo": "CORREO", "telefono": "TELEFONO",
        }
        campos, valores = [], []
        for campo_py, campo_sql in mapeo.items():
            valor = getattr(datos, campo_py)
            if valor is not None:
                campos.append(f"{campo_sql} = %s")
                valores.append(valor)
        if not campos:
            raise HTTPException(status_code=400, detail="No se enviaron campos para actualizar")
        valores.append(cliente_id)
        cursor.execute(f"UPDATE CLIENTES SET {', '.join(campos)} WHERE CLIENTE_ID = %s", tuple(valores))
        conn.commit()
        return {"id": cliente_id, "mensaje": "Cliente actualizado"}
    finally:
        conn.close()


@router.delete("/{cliente_id}")
def eliminar_cliente(cliente_id: str):
    conn = get_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM CLIENTES WHERE CLIENTE_ID = %s", (cliente_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Cliente no encontrado")
        try:
            cursor.execute("DELETE FROM CLIENTES WHERE CLIENTE_ID = %s", (cliente_id,))
            conn.commit()
        except Exception:
            raise HTTPException(
                status_code=400,
                detail="No se pudo eliminar: el cliente tiene préstamos asociados",
            )
        return {"mensaje": "Cliente eliminado"}
    finally:
        conn.close()