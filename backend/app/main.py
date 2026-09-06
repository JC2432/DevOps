from fastapi import FastAPI
from .routers import prestamos, libros, usuarios, autores, editorial, categorias, clientes

app = FastAPI(
    title="Sistema de Préstamos/Biblioteca",
    description="API REST del proyecto de Habilidades DevOps",
    version="1.0.0",
)

app.include_router(prestamos.router)
app.include_router(libros.router)
app.include_router(usuarios.router)
app.include_router(autores.router)
app.include_router(editorial.router)
app.include_router(categorias.router)
app.include_router(clientes.router)


@app.get("/")
def root():
    return {"mensaje": "API del Sistema de Préstamos/Biblioteca. Ver /docs"}


@app.get("/health")
def health_check():
    """Endpoint simple para verificar que el servicio está arriba (útil para CI)."""
    return {"status": "ok"}
