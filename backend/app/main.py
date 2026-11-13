import os

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from mysql.connector import errors as mysql_errors

from .routers import (
    auth, autores, categorias, clientes, editorial, libros, portal, prestamos, usuarios,
)

app = FastAPI(
    title="Sistema de Préstamos/Biblioteca",
    description=(
        "API REST del proyecto de Habilidades DevOps.\n\n"
        "Casi todos los endpoints requieren sesión: usa `POST /login` y luego el botón "
        "**Authorize** con el `token` que devuelve."
    ),
    version="2.0.0",
)

# Orígenes permitidos, separados por coma (ej. "http://localhost:5500").
# Por defecto "*" (desarrollo). La sesión viaja en el header Authorization, no en cookies,
# así que no se permiten credenciales.
ORIGENES = [o.strip() for o in os.getenv("CORS_ORIGINS", "*").split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ORIGENES,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(portal.router)
app.include_router(prestamos.router)
app.include_router(libros.router)
app.include_router(usuarios.router)
app.include_router(clientes.router)
app.include_router(autores.router)
app.include_router(editorial.router)
app.include_router(categorias.router)

# Errores de MySQL por datos inválidos -> mensaje claro en vez de un 500.
# https://dev.mysql.com/doc/mysql-errors/8.0/en/server-error-reference.html
_ERRORES_INTEGRIDAD = {
    1062: (409, "Ya existe un registro con ese valor (ID, correo o usuario repetido)"),
    1451: (409, "No se puede eliminar porque otros registros dependen de él "
                "(por ejemplo, préstamos o libros asociados)"),
    1452: (400, "Alguna referencia no existe (revisa la editorial, el cargo o el cliente)"),
    3819: (400, "Los datos no cumplen las reglas de la base de datos (revisa las fechas)"),
}


@app.exception_handler(mysql_errors.IntegrityError)
@app.exception_handler(mysql_errors.DatabaseError)
async def error_de_datos(request: Request, exc: mysql_errors.Error):
    if exc.errno in _ERRORES_INTEGRIDAD:
        status, mensaje = _ERRORES_INTEGRIDAD[exc.errno]
        return JSONResponse(status_code=status, content={"detail": mensaje})
    # Cualquier otro error de la BD (p. ej. MySQL apagado) sí es un error del servidor
    return JSONResponse(
        status_code=500, content={"detail": "Error en la base de datos. Intenta de nuevo."}
    )


@app.get("/")
def root():
    return {"mensaje": "API del Sistema de Préstamos/Biblioteca. Ver /docs"}


@app.get("/health")
def health_check():
    """Endpoint simple para verificar que el servicio está arriba (útil para CI)."""
    return {"status": "ok"}
