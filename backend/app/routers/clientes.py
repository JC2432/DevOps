from fastapi import APIRouter, HTTPException
from ..database import get_connection

router = APIRouter(prefix="/clientes", tags=["clientes"])


@router.get("/")
def obtener_clientes():
    """Devuelve la lista de clientes."""
    conn = get_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM CLIENTES")
        resultados = cursor.fetchall()
        return {"clientes": resultados}
    finally:
        conn.close()

@router.get("/{cliente_id}")
def obtener_cliente(cliente_id: str):
    """Devuelve un cliente específico por su id (CLIENTE_ID, ej. 'C001')."""
    conn = get_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT * FROM CLIENTES WHERE CLIENTE_ID = %s",
            (cliente_id,),
        )
        resultado = cursor.fetchone()
        if not resultado:
            raise HTTPException(status_code=404, detail="Cliente no encontrado")
        return resultado
    finally:
        conn.close()