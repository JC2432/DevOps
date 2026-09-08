from fastapi import APIRouter, HTTPException
from ..database import get_connection
from ..schemas import UsuarioIn, UsuarioUpdateIn

router = APIRouter(prefix="/usuarios", tags=["usuarios"])

CAMPOS_USUARIO = """
    u.USUARIO_ID AS id,
    u.CARGO_ID AS cargo_id,
    c.PUESTO AS cargo,
    u.USERNAME AS username,
    u.NOMBRE AS nombre,
    u.APELLIDO_P AS apellido_p,
    u.APELLIDO_M AS apellido_m
"""
# Nota: nunca seleccionamos PASSWORD, ni siquiera para el formulario de edición
# (buena práctica: al editar, el campo de contraseña queda vacío por defecto).


@router.get("/")
def obtener_usuarios():
    conn = get_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            f"SELECT {CAMPOS_USUARIO} FROM USUARIOS u JOIN CARGO c ON u.CARGO_ID = c.CARGO_ID"
        )
        return cursor.fetchall()
    finally:
        conn.close()


@router.get("/{usuario_id}")
def obtener_usuario(usuario_id: str):
    conn = get_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            f"SELECT {CAMPOS_USUARIO} FROM USUARIOS u JOIN CARGO c ON u.CARGO_ID = c.CARGO_ID "
            f"WHERE u.USUARIO_ID = %s",
            (usuario_id,),
        )
        resultado = cursor.fetchone()
        if not resultado:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        return resultado
    finally:
        conn.close()


@router.post("/", status_code=201)
def crear_usuario(usuario: UsuarioIn):
    conn = get_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT USUARIO_ID FROM USUARIOS WHERE USUARIO_ID = %s", (usuario.id,))
        if cursor.fetchone():
            raise HTTPException(status_code=400, detail="Ya existe un usuario con ese ID")
        cursor.execute(
            """
            INSERT INTO USUARIOS (USUARIO_ID, CARGO_ID, USERNAME, PASSWORD, NOMBRE, APELLIDO_P, APELLIDO_M)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """,
            (
                usuario.id, usuario.cargo_id, usuario.username, usuario.password,
                usuario.nombre, usuario.apellido_p, usuario.apellido_m,
            ),
        )
        conn.commit()
        return {"id": usuario.id, "mensaje": "Usuario creado"}
    finally:
        conn.close()


@router.put("/{usuario_id}")
def actualizar_usuario(usuario_id: str, datos: UsuarioUpdateIn):
    conn = get_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM USUARIOS WHERE USUARIO_ID = %s", (usuario_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Usuario no encontrado")

        mapeo = {
            "cargo_id": "CARGO_ID", "username": "USERNAME", "password": "PASSWORD",
            "nombre": "NOMBRE", "apellido_p": "APELLIDO_P", "apellido_m": "APELLIDO_M",
        }
        campos, valores = [], []
        for campo_py, campo_sql in mapeo.items():
            valor = getattr(datos, campo_py)
            if valor is not None and valor != "":
                campos.append(f"{campo_sql} = %s")
                valores.append(valor)
        if not campos:
            raise HTTPException(status_code=400, detail="No se enviaron campos para actualizar")
        valores.append(usuario_id)
        cursor.execute(f"UPDATE USUARIOS SET {', '.join(campos)} WHERE USUARIO_ID = %s", tuple(valores))
        conn.commit()
        return {"id": usuario_id, "mensaje": "Usuario actualizado"}
    finally:
        conn.close()


@router.delete("/{usuario_id}")
def eliminar_usuario(usuario_id: str):
    conn = get_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM USUARIOS WHERE USUARIO_ID = %s", (usuario_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        try:
            cursor.execute("DELETE FROM USUARIOS WHERE USUARIO_ID = %s", (usuario_id,))
            conn.commit()
        except Exception:
            raise HTTPException(
                status_code=400,
                detail="No se pudo eliminar: el usuario tiene préstamos asociados",
            )
        return {"mensaje": "Usuario eliminado"}
    finally:
        conn.close()