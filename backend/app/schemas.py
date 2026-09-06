from pydantic import BaseModel
from typing import Optional, List
from datetime import date


class ClienteCreate(BaseModel):
    NOMBRE: str
    APELLIDO_P: str
    APELLIDO_M: Optional[str] = None
    CORREO: str
    TELEFONO: Optional[str] = None


class LibroCreate(BaseModel):
    EDITORIAL_ID: str
    TITULO: str
    ANIO_PUBLICACION: Optional[int] = None
    DISPONIBLE: Optional[bool] = True


class LibroUpdate(BaseModel):
    DISPONIBLE: bool


class LibroPrestamoItem(BaseModel):
    LIBRO_ID: str
    CANTIDAD: Optional[int] = 1


class PrestamoCreate(BaseModel):
    CLIENTE_ID: str
    USUARIO_ID: str
    FECHA_PRESTAMO: date
    libros: List[LibroPrestamoItem]