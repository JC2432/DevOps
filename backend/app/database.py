"""
Módulo de conexión a MySQL.

Ajusta los valores de conexión según lo que defina el encargado de base
de datos (host, usuario, contraseña, nombre de la BD). Se recomienda
usar variables de entorno en lugar de valores fijos en el código.
"""

import os
import mysql.connector
from dotenv import load_dotenv
load_dotenv()  # Carga las variables de entorno desde el archivo .env
from mysql.connector import pooling

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": int(os.getenv("DB_PORT", "3306")),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", ""),
    "database": os.getenv("DB_NAME", "biblioteca"),
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
