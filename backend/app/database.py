"""
Módulo de conexión a MySQL.

Los valores de conexión se leen de variables de entorno (ver .env.example).
"""

import os

from dotenv import load_dotenv
from mysql.connector import pooling

load_dotenv()  # Carga las variables de entorno desde el archivo .env

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": int(os.getenv("DB_PORT", "3306")),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", ""),
    "database": os.getenv("DB_NAME", "biblioteca_db"),
}

_pool = None


def get_pool():
    global _pool
    if _pool is None:
        _pool = pooling.MySQLConnectionPool(
            pool_name="app_pool",
            pool_size=5,
            **DB_CONFIG,
        )
    return _pool


def get_connection():
    """Devuelve una conexión del pool. Recuerda cerrarla después de usarla."""
    return get_pool().get_connection()


def generar_siguiente_id(cursor, tabla, columna_id, prefijo, ancho_numero):
    """
    Genera el siguiente ID disponible con un prefijo dado.
    Ej: generar_siguiente_id(cursor, "CLIENTES", "CLIENTE_ID", "C", 3) -> "C003"

    Ordena por la parte numérica (no como texto), para que 'X100' > 'X99'.
    Nota: el ancho está limitado por el CHAR(4) del esquema (máx. 'LP99' / 'P999').
    """
    inicio = len(prefijo) + 1
    cursor.execute(
        f"SELECT {columna_id} FROM {tabla} "
        f"WHERE {columna_id} LIKE %s "
        f"ORDER BY CAST(SUBSTRING({columna_id}, {inicio}) AS UNSIGNED) DESC LIMIT 1",
        (f"{prefijo}%",),
    )
    fila = cursor.fetchone()
    if fila:
        ultimo_id = fila[0] if not isinstance(fila, dict) else fila[columna_id]
        numero = int(ultimo_id[len(prefijo):]) + 1
    else:
        numero = 1
    return f"{prefijo}{numero:0{ancho_numero}d}"
