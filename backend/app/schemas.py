"""Modelos de entrada de la API. Pydantic rechaza con 422 los datos que no cumplen."""

from datetime import date
from typing import Annotated, List, Optional

from pydantic import BaseModel, ConfigDict, Field, model_validator

# Tipos reutilizables
IdCorto = Annotated[str, Field(pattern=r"^[A-Za-z0-9]{1,4}$", description="Ej. 'L001'")]
Texto20 = Annotated[str, Field(min_length=1, max_length=20)]
Texto30 = Annotated[str, Field(min_length=1, max_length=30)]
Texto50 = Annotated[str, Field(min_length=1, max_length=50)]
Correo = Annotated[str, Field(max_length=50, pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$")]
Telefono = Annotated[str, Field(max_length=20, pattern=r"^[0-9 +()-]*$")]
Password = Annotated[str, Field(min_length=6, max_length=128)]
Anio = Annotated[int, Field(ge=0, le=2100)]


class Entrada(BaseModel):
    # Quita espacios al inicio y al final de todos los textos
    model_config = ConfigDict(str_strip_whitespace=True)


class LoginIn(Entrada):
    username: str  # para clientes es su correo
    password: str
    # "CLIENTE", "BIBLIOTECARIO" o "ADMINISTRADOR". Si no se manda, se busca en el personal.
    cargo: Optional[str] = None


class LibroIn(Entrada):
    id: IdCorto
    editorial_id: IdCorto
    titulo: Annotated[str, Field(min_length=1, max_length=100)]
    anio: Optional[Anio] = None
    disponible: bool = True


class LibroUpdateIn(Entrada):
    editorial_id: Optional[IdCorto] = None
    titulo: Optional[Annotated[str, Field(min_length=1, max_length=100)]] = None
    anio: Optional[Anio] = None
    disponible: Optional[bool] = None


class UsuarioIn(Entrada):
    id: IdCorto
    cargo_id: IdCorto
    username: Texto20
    password: Password
    nombre: Texto20
    apellido_p: Texto20
    apellido_m: Optional[Annotated[str, Field(max_length=20)]] = None


class UsuarioUpdateIn(Entrada):
    cargo_id: Optional[IdCorto] = None
    username: Optional[Texto20] = None
    password: Optional[Password] = None
    nombre: Optional[Texto20] = None
    apellido_p: Optional[Texto20] = None
    apellido_m: Optional[Annotated[str, Field(max_length=20)]] = None


class ClienteIn(Entrada):
    id: IdCorto
    nombre: Texto50
    apellido_p: Texto30
    apellido_m: Optional[Annotated[str, Field(max_length=30)]] = None
    correo: Correo
    telefono: Optional[Telefono] = None
    # Opcional: si se manda, el cliente puede entrar al portal con su correo
    password: Optional[Password] = None


class ClienteUpdateIn(Entrada):
    nombre: Optional[Texto50] = None
    apellido_p: Optional[Texto30] = None
    apellido_m: Optional[Annotated[str, Field(max_length=30)]] = None
    correo: Optional[Correo] = None
    telefono: Optional[Telefono] = None
    password: Optional[Password] = None


class CategoriaIn(Entrada):
    id: IdCorto
    nombre: Texto30


class CategoriaUpdateIn(Entrada):
    nombre: Texto30


ListaLibros = Annotated[List[IdCorto], Field(min_length=1, max_length=5)]


class PrestamoIn(Entrada):
    """Préstamo registrado en mostrador: el cliente se lleva los libros en ese momento."""

    cliente_id: IdCorto
    libros: ListaLibros
    fecha_prestamo: Optional[date] = None  # por defecto, hoy
    fecha_limite: Optional[date] = None    # por defecto, fecha_prestamo + 14 días

    @model_validator(mode="after")
    def _fechas_en_orden(self):
        if self.fecha_prestamo and self.fecha_limite and self.fecha_limite < self.fecha_prestamo:
            raise ValueError("La fecha límite no puede ser anterior a la fecha del préstamo")
        return self


class PrestamoUpdateIn(Entrada):
    """Corrección de fechas o renovación (ampliar la fecha límite)."""

    fecha_prestamo: Optional[date] = None
    fecha_limite: Optional[date] = None


class ApartadoIn(Entrada):
    """Libros que un cliente aparta desde el portal para recogerlos en la biblioteca."""

    libros: ListaLibros
