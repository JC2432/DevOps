from fastapi import APIRouter, Depends, HTTPException

from ..database import actualizar_campos
from ..dependencias import get_db, solo_personal
from ..schemas import UsuarioIn, UsuarioUpdateIn
from ..seguridad import hash_password

# Cuentas del personal: solo el personal (bibliotecarios y administradores) las gestiona.
router = APIRouter(prefix="/usuarios", tags=["usuarios"], dependencies=[Depends(solo_personal)])

# Nunca seleccionamos PASSWORD, ni siquiera para el formulario de edición
# (al editar, el campo de contraseña queda vacío por defecto).
CONSULTA = """
    SELECT u.USUARIO_ID AS id,
           u.CARGO_ID AS cargo_id,
           c.PUESTO AS cargo,
           u.USERNAME AS username,
           u.NOMBRE AS nombre,
           u.APELLIDO_P AS apellido_p,
           u.APELLIDO_M AS apellido_m
    FROM USUARIOS u JOIN CARGO c ON u.CARGO_ID = c.CARGO_ID
"""


@router.get("/cargos")
def obtener_cargos(conn=Depends(get_db)):
    """Lista de cargos para llenar el selector del formulario."""
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT CARGO_ID AS id, PUESTO AS puesto FROM CARGO ORDER BY CARGO_ID")
    return cursor.fetchall()


@router.get("/")
def obtener_usuarios(conn=Depends(get_db)):
    cursor = conn.cursor(dictionary=True)
    cursor.execute(f"{CONSULTA} ORDER BY u.USUARIO_ID")
    return cursor.fetchall()


@router.get("/{usuario_id}")
def obtener_usuario(usuario_id: str, conn=Depends(get_db)):
    cursor = conn.cursor(dictionary=True)
    cursor.execute(f"{CONSULTA} WHERE u.USUARIO_ID = %s", (usuario_id,))
    resultado = cursor.fetchone()
    if not resultado:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return resultado


@router.post("/", status_code=201)
def crear_usuario(usuario: UsuarioIn, conn=Depends(get_db)):
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO USUARIOS
            (USUARIO_ID, CARGO_ID, USERNAME, PASSWORD, NOMBRE, APELLIDO_P, APELLIDO_M)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """,
        (
            usuario.id, usuario.cargo_id, usuario.username,
            hash_password(usuario.password),
            usuario.nombre, usuario.apellido_p, usuario.apellido_m or None,
        ),
    )
    conn.commit()
    return {"id": usuario.id, "mensaje": "Usuario creado"}


@router.put("/{usuario_id}")
def actualizar_usuario(usuario_id: str, datos: UsuarioUpdateIn, conn=Depends(get_db)):
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM USUARIOS WHERE USUARIO_ID = %s", (usuario_id,))
    if not cursor.fetchone():
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    if datos.password:
        datos = datos.model_copy(update={"password": hash_password(datos.password)})
    mapeo = {
        "cargo_id": "CARGO_ID", "username": "USERNAME", "password": "PASSWORD",
        "nombre": "NOMBRE", "apellido_p": "APELLIDO_P", "apellido_m": "APELLIDO_M",
    }
    if not actualizar_campos(cursor, "USUARIOS", "USUARIO_ID", usuario_id, datos, mapeo):
        raise HTTPException(status_code=400, detail="No se enviaron campos para actualizar")
    conn.commit()
    return {"id": usuario_id, "mensaje": "Usuario actualizado"}


@router.delete("/{usuario_id}")
def eliminar_usuario(usuario_id: str, sesion: dict = Depends(solo_personal),
                     conn=Depends(get_db)):
    if usuario_id == sesion["sub"]:
        raise HTTPException(status_code=400, detail="No puedes eliminar tu propia cuenta")
    cursor = conn.cursor()
    # Si el usuario atendió préstamos, MySQL lo impide y la API responde 409.
    cursor.execute("DELETE FROM USUARIOS WHERE USUARIO_ID = %s", (usuario_id,))
    if cursor.rowcount == 0:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    conn.commit()
    return {"mensaje": "Usuario eliminado"}
