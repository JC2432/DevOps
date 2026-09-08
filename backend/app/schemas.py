from pydantic import BaseModel
from typing import Optional, List
from datetime import date


class LibroPrestamoItem(BaseModel):
    LIBRO_ID: str
    CANTIDAD: Optional[int] = 1


class LibroIn(BaseModel):
    id: str
    editorial_id: str
    titulo: str
    anio: Optional[int] = None
    disponible: Optional[bool] = True


class LibroUpdateIn(BaseModel):
    editorial_id: Optional[str] = None
    titulo: Optional[str] = None
    anio: Optional[int] = None
    disponible: Optional[bool] = None


class UsuarioIn(BaseModel):
    id: str
    cargo_id: str
    username: str
    password: str
    nombre: str
    apellido_p: str
    apellido_m: Optional[str] = None


class UsuarioUpdateIn(BaseModel):
    cargo_id: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None
    nombre: Optional[str] = None
    apellido_p: Optional[str] = None
    apellido_m: Optional[str] = None


class ClienteIn(BaseModel):
    id: str
    nombre: str
    apellido_p: str
    apellido_m: Optional[str] = None
    correo: str
    telefono: Optional[str] = None


class ClienteUpdateIn(BaseModel):
    nombre: Optional[str] = None
    apellido_p: Optional[str] = None
    apellido_m: Optional[str] = None
    correo: Optional[str] = None
    telefono: Optional[str] = None


class CategoriaIn(BaseModel):
    id: str
    nombre: str


class CategoriaUpdateIn(BaseModel):
    nombre: str


class PrestamoIn(BaseModel):
    id: Optional[str] = None
    estado_prestamos_id: str
    cliente_id: str
    usuario_id: str
    fecha_prestamo: date
    fecha_devolucion: Optional[date] = None
    libros: Optional[List[LibroPrestamoItem]] = None


class PrestamoUpdateIn(BaseModel):
    estado_prestamos_id: Optional[str] = None
    cliente_id: Optional[str] = None
    usuario_id: Optional[str] = None
    fecha_prestamo: Optional[date] = None
    fecha_devolucion: Optional[date] = None