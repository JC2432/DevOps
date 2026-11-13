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
            pool_size=int(os.getenv("DB_POOL_SIZE", "10")),
            **DB_CONFIG,
        )
    return _pool


def get_connection():
    """Devuelve una conexión del pool. Recuerda cerrarla después de usarla."""
    return get_pool().get_connection()


def actualizar_campos(cursor, tabla, columna_id, valor_id, datos, mapeo):
    """UPDATE parcial: solo cambia los campos del modelo `datos` que no vienen en None.

    `mapeo` traduce el nombre del campo en la API al nombre de la columna en MySQL.
    Devuelve cuántos campos se actualizaron (0 si no se mandó ninguno).
    """
    campos, valores = [], []
    for campo_api, columna in mapeo.items():
        valor = getattr(datos, campo_api)
        if valor is not None:
            campos.append(f"{columna} = %s")
            valores.append(valor)
    if campos:
        cursor.execute(
            f"UPDATE {tabla} SET {', '.join(campos)} WHERE {columna_id} = %s",
            (*valores, valor_id),
        )
    return len(campos)


def generar_siguiente_id(cursor, tabla, columna_id, prefijo, ancho_numero):
    """
    Genera el siguiente ID disponible con un prefijo dado.
    Ej: generar_siguiente_id(cursor, "PRESTAMOS", "PRESTAMO_ID", "P", 3) -> "P004"

    Ordena por la parte numérica (no como texto), para que 'P1000' > 'P999'. El número
    crece más allá del ancho si hace falta, así que la columna debe tener espacio
    (PRESTAMO_ID es VARCHAR(10)). FOR UPDATE evita que dos peticiones simultáneas
    obtengan el mismo ID.
    """
    inicio = len(prefijo) + 1
    cursor.execute(
        f"SELECT {columna_id} FROM {tabla} "
        f"WHERE {columna_id} LIKE %s "
        f"ORDER BY CAST(SUBSTRING({columna_id}, {inicio}) AS UNSIGNED) DESC LIMIT 1 "
        f"FOR UPDATE",
        (f"{prefijo}%",),
    )
    fila = cursor.fetchone()
    if fila:
        ultimo_id = fila[0] if not isinstance(fila, dict) else fila[columna_id]
        numero = int(ultimo_id[len(prefijo):]) + 1
    else:
        numero = 1
    return f"{prefijo}{numero:0{ancho_numero}d}"
