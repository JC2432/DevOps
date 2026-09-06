from fastapi import APIRouter, HTTPException
from ..database import get_connection, generar_siguiente_id
from ..schemas import ClienteCreate

router = APIRouter(prefix="/clientes", tags=["clientes"])


@router.get("/")
def obtener_clientes():
    """Devuelve la lista de clientes."""
    conn = get_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM CLIENTES")
        return {"clientes": cursor.fetchall()}
    finally:
        conn.close()


@router.get("/{cliente_id}")
def obtener_cliente(cliente_id: str):
    """Devuelve un cliente específico por su id."""
    conn = get_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM CLIENTES WHERE CLIENTE_ID = %s", (cliente_id,))
        resultado = cursor.fetchone()
        if not resultado:
            raise HTTPException(status_code=404, detail="Cliente no encontrado")
        return resultado
    finally:
        conn.close()


@router.post("/", status_code=201)
def crear_cliente(cliente: ClienteCreate):
    """Registra un nuevo cliente."""
    conn = get_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        nuevo_id = generar_siguiente_id(cursor, "CLIENTES", "CLIENTE_ID", "C", 3)
        cursor.execute(
            """
            INSERT INTO CLIENTES (CLIENTE_ID, NOMBRE, APELLIDO_P, APELLIDO_M, CORREO, TELEFONO)
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (
                nuevo_id,
                cliente.NOMBRE,
                cliente.APELLIDO_P,
                cliente.APELLIDO_M,
                cliente.CORREO,
                cliente.TELEFONO,
            ),
        )
        conn.commit()
        return {"CLIENTE_ID": nuevo_id, **cliente.model_dump()}
    finally:
        conn.close()