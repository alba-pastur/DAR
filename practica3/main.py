from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field
from typing import Optional
import re

# ──────────────────────────────────────────────────────────────────────────────
# Aplicación FastAPI
# ──────────────────────────────────────────────────────────────────────────────

app = FastAPI(
    title="Chat Multiusuario con Salas",
    description=(
        "API REST para un sistema de chat multiusuario con salas. "
        "Permite registrar usuarios, iniciar sesión, gestionar salas "
        "y enviar/recibir mensajes. Transformación de la Práctica 2 (Java RMI) a REST."
    ),
    version="1.0.0",
    contact={"name": "DAR - Desarrollo de Aplicaciones en Red"},
)

# ──────────────────────────────────────────────────────────────────────────────
# Estado del servidor (equivalente al estado compartido de la Práctica 2)
# ──────────────────────────────────────────────────────────────────────────────

usuarios: dict[str, str] = {}           # username -> password
sesiones_activas: set[str] = set()      # usernames con sesión abierta
salas: dict[str, set[str]] = {}         # roomname -> set de usernames
mensajes: dict[str, list[dict]] = {}    # roomname -> lista de mensajes
ultimo_leido: dict[str, int] = {}       # "username:roomname" -> índice

# ──────────────────────────────────────────────────────────────────────────────
# Modelos Pydantic
# ──────────────────────────────────────────────────────────────────────────────

class RegistroRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=16, pattern=r'^[A-Za-z0-9]+$',
                          description="Nombre de usuario (3-16 caracteres alfanuméricos)")
    password: str = Field(..., min_length=4, max_length=32,
                          description="Contraseña (4-32 caracteres)")

    model_config = {"json_schema_extra": {"example": {"username": "alba", "password": "1234"}}}


class LoginRequest(BaseModel):
    username: str = Field(..., description="Nombre de usuario")
    password: str = Field(..., description="Contraseña")

    model_config = {"json_schema_extra": {"example": {"username": "alba", "password": "1234"}}}


class CrearSalaRequest(BaseModel):
    username: str = Field(..., description="Usuario que crea la sala (debe tener sesión activa)")
    roomname: str = Field(..., min_length=3, max_length=20,
                          pattern=r'^[A-Za-z0-9\-_]+$',
                          description="Nombre de sala (3-20 caracteres)")

    model_config = {"json_schema_extra": {"example": {"username": "alba", "roomname": "general"}}}


class UnirseRequest(BaseModel):
    username: str = Field(..., description="Usuario que se une (debe tener sesión activa)")

    model_config = {"json_schema_extra": {"example": {"username": "alba"}}}


class MensajeRequest(BaseModel):
    username: str = Field(..., description="Usuario que envía el mensaje")
    text: str = Field(..., min_length=1, description="Texto del mensaje")

    model_config = {"json_schema_extra": {"example": {"username": "alba", "text": "Hola a todos!"}}}


# ──────────────────────────────────────────────────────────────────────────────
# Helpers de validación
# ──────────────────────────────────────────────────────────────────────────────

def verificar_sesion(username: str):
    if username not in sesiones_activas:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail=f"El usuario '{username}' no tiene sesión activa")

def verificar_sala(roomname: str):
    if roomname not in salas:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"La sala '{roomname}' no existe")

# ──────────────────────────────────────────────────────────────────────────────
# RAÍZ
# ──────────────────────────────────────────────────────────────────────────────

@app.get("/", summary="Raíz", description="Endpoint de bienvenida y estado del servicio",
         tags=["General"])
def root():
    return {
        "servicio": "Chat Multiusuario con Salas",
        "version": "1.0.0",
        "estado": "activo",
        "usuarios_conectados": len(sesiones_activas),
        "salas_activas": len(salas),
    }

# ──────────────────────────────────────────────────────────────────────────────
# USUARIOS  →  /users
# ──────────────────────────────────────────────────────────────────────────────

@app.post(
    "/users",
    status_code=status.HTTP_201_CREATED,
    summary="Registrar un nuevo usuario",
    description=(
        "Registra un nuevo usuario en el sistema. "
        "El nombre de usuario debe tener entre 3 y 16 caracteres alfanuméricos. "
        "La contraseña entre 4 y 32 caracteres. "
        "Equivalente a REGISTER del protocolo original."
    ),
    tags=["Usuarios"],
    responses={
        201: {"description": "Usuario registrado correctamente"},
        400: {"description": "Datos inválidos"},
        409: {"description": "El usuario ya existe"},
    }
)
def registrar_usuario(body: RegistroRequest):
    if body.username in usuarios:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail=f"El usuario '{body.username}' ya está registrado")
    usuarios[body.username] = body.password
    return {"mensaje": "Usuario registrado correctamente", "username": body.username}


@app.get(
    "/users",
    summary="Listar usuarios registrados",
    description="Devuelve la lista de todos los usuarios registrados en el sistema.",
    tags=["Usuarios"]
)
def listar_usuarios():
    return {
        "total": len(usuarios),
        "usuarios": list(usuarios.keys()),
        "conectados": list(sesiones_activas)
    }

# ──────────────────────────────────────────────────────────────────────────────
# SESIONES  →  /sessions
# ──────────────────────────────────────────────────────────────────────────────

@app.post(
    "/sessions",
    status_code=status.HTTP_201_CREATED,
    summary="Iniciar sesión",
    description=(
        "Autentica al usuario y abre una sesión. "
        "Equivalente a LOGIN del protocolo original."
    ),
    tags=["Sesiones"],
    responses={
        201: {"description": "Sesión iniciada correctamente"},
        401: {"description": "Contraseña incorrecta"},
        404: {"description": "Usuario no encontrado"},
        409: {"description": "El usuario ya tiene sesión activa"},
    }
)
def iniciar_sesion(body: LoginRequest):
    if body.username not in usuarios:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"El usuario '{body.username}' no existe")
    if usuarios[body.username] != body.password:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Contraseña incorrecta")
    if body.username in sesiones_activas:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail=f"El usuario '{body.username}' ya tiene sesión activa")
    sesiones_activas.add(body.username)
    return {"mensaje": "Sesión iniciada correctamente", "username": body.username}


@app.delete(
    "/sessions/{username}",
    summary="Cerrar sesión",
    description=(
        "Cierra la sesión del usuario y lo elimina de todas las salas en las que participa. "
        "Equivalente a QUIT del protocolo original."
    ),
    tags=["Sesiones"],
    responses={
        200: {"description": "Sesión cerrada correctamente"},
        404: {"description": "El usuario no tiene sesión activa"},
    }
)
def cerrar_sesion(username: str):
    if username not in sesiones_activas:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"El usuario '{username}' no tiene sesión activa")
    sesiones_activas.discard(username)
    for roomname, miembros in salas.items():
        if username in miembros:
            miembros.discard(username)
            mensajes[roomname].append({
                "tipo": "EVT_ROOM_UPDATE",
                "sala": roomname,
                "accion": "LEAVE",
                "usuario": username
            })
    return {"mensaje": f"Sesión de '{username}' cerrada correctamente"}


@app.get(
    "/sessions",
    summary="Listar sesiones activas",
    description="Devuelve la lista de usuarios con sesión activa en este momento.",
    tags=["Sesiones"]
)
def listar_sesiones():
    return {"sesiones_activas": list(sesiones_activas), "total": len(sesiones_activas)}

# ──────────────────────────────────────────────────────────────────────────────
# SALAS  →  /rooms
# ──────────────────────────────────────────────────────────────────────────────

@app.post(
    "/rooms",
    status_code=status.HTTP_201_CREATED,
    summary="Crear una sala",
    description=(
        "Crea una nueva sala de chat. El usuario debe tener sesión activa. "
        "El nombre de sala admite letras, números, guiones y guiones bajos (3-20 caracteres). "
        "Equivalente a ROOM_CREATE del protocolo original."
    ),
    tags=["Salas"],
    responses={
        201: {"description": "Sala creada correctamente"},
        400: {"description": "Nombre de sala inválido"},
        401: {"description": "Usuario sin sesión activa"},
        409: {"description": "La sala ya existe"},
    }
)
def crear_sala(body: CrearSalaRequest):
    verificar_sesion(body.username)
    if body.roomname in salas:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail=f"La sala '{body.roomname}' ya existe")
    salas[body.roomname] = set()
    mensajes[body.roomname] = []
    return {"mensaje": "Sala creada correctamente", "sala": body.roomname, "creador": body.username}


@app.get(
    "/rooms",
    summary="Listar todas las salas",
    description="Devuelve la lista de salas disponibles con el número de miembros en cada una.",
    tags=["Salas"]
)
def listar_salas():
    return {
        "total": len(salas),
        "salas": [
            {"nombre": name, "miembros": len(members)}
            for name, members in salas.items()
        ]
    }


@app.get(
    "/rooms/{roomname}",
    summary="Obtener información de una sala",
    description="Devuelve los detalles de una sala: miembros y número de mensajes.",
    tags=["Salas"],
    responses={
        200: {"description": "Información de la sala"},
        404: {"description": "Sala no encontrada"},
    }
)
def obtener_sala(roomname: str):
    verificar_sala(roomname)
    return {
        "sala": roomname,
        "miembros": list(salas[roomname]),
        "total_miembros": len(salas[roomname]),
        "total_mensajes": len(mensajes[roomname]),
    }


@app.delete(
    "/rooms/{roomname}",
    summary="Eliminar una sala",
    description=(
        "Elimina una sala existente. El usuario debe tener sesión activa. "
        "Equivalente a ROOM_DELETE del protocolo original."
    ),
    tags=["Salas"],
    responses={
        200: {"description": "Sala eliminada correctamente"},
        401: {"description": "Usuario sin sesión activa"},
        404: {"description": "Sala no encontrada"},
    }
)
def eliminar_sala(roomname: str, username: str):
    verificar_sesion(username)
    verificar_sala(roomname)
    del salas[roomname]
    del mensajes[roomname]
    return {"mensaje": f"Sala '{roomname}' eliminada correctamente"}

# ──────────────────────────────────────────────────────────────────────────────
# MIEMBROS  →  /rooms/{roomname}/members
# ──────────────────────────────────────────────────────────────────────────────

@app.post(
    "/rooms/{roomname}/members",
    status_code=status.HTTP_201_CREATED,
    summary="Unirse a una sala",
    description=(
        "Añade al usuario como miembro de la sala. "
        "El usuario debe tener sesión activa. "
        "Equivalente a ROOM_JOIN del protocolo original."
    ),
    tags=["Miembros"],
    responses={
        201: {"description": "Usuario unido a la sala"},
        401: {"description": "Usuario sin sesión activa"},
        404: {"description": "Sala no encontrada"},
        409: {"description": "El usuario ya está en la sala"},
    }
)
def unirse_sala(roomname: str, body: UnirseRequest):
    verificar_sesion(body.username)
    verificar_sala(roomname)
    if body.username in salas[roomname]:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail=f"'{body.username}' ya está en la sala '{roomname}'")
    salas[roomname].add(body.username)
    mensajes[roomname].append({
        "tipo": "EVT_ROOM_UPDATE",
        "sala": roomname,
        "accion": "JOIN",
        "usuario": body.username
    })
    ultimo_leido[f"{body.username}:{roomname}"] = len(mensajes[roomname])
    return {"mensaje": f"'{body.username}' se ha unido a '{roomname}'", "sala": roomname}


@app.get(
    "/rooms/{roomname}/members",
    summary="Listar miembros de una sala",
    description=(
        "Devuelve la lista de usuarios que están actualmente en la sala. "
        "Equivalente a GET_USERS del protocolo original."
    ),
    tags=["Miembros"],
    responses={
        200: {"description": "Lista de miembros"},
        404: {"description": "Sala no encontrada"},
    }
)
def listar_miembros(roomname: str):
    verificar_sala(roomname)
    return {
        "sala": roomname,
        "miembros": list(salas[roomname]),
        "total": len(salas[roomname])
    }


@app.delete(
    "/rooms/{roomname}/members/{username}",
    summary="Abandonar una sala",
    description=(
        "Elimina al usuario de la sala. "
        "Equivalente a ROOM_LEAVE del protocolo original."
    ),
    tags=["Miembros"],
    responses={
        200: {"description": "Usuario ha abandonado la sala"},
        401: {"description": "Usuario sin sesión activa"},
        404: {"description": "Sala o usuario no encontrado"},
    }
)
def abandonar_sala(roomname: str, username: str):
    verificar_sesion(username)
    verificar_sala(roomname)
    if username not in salas[roomname]:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"'{username}' no está en la sala '{roomname}'")
    salas[roomname].discard(username)
    mensajes[roomname].append({
        "tipo": "EVT_ROOM_UPDATE",
        "sala": roomname,
        "accion": "LEAVE",
        "usuario": username
    })
    return {"mensaje": f"'{username}' ha abandonado '{roomname}'"}

# ──────────────────────────────────────────────────────────────────────────────
# MENSAJES  →  /rooms/{roomname}/messages
# ──────────────────────────────────────────────────────────────────────────────

@app.post(
    "/rooms/{roomname}/messages",
    status_code=status.HTTP_201_CREATED,
    summary="Enviar un mensaje a una sala",
    description=(
        "Publica un mensaje en la sala. "
        "El usuario debe tener sesión activa y ser miembro de la sala. "
        "Equivalente a MSG_SEND del protocolo original."
    ),
    tags=["Mensajes"],
    responses={
        201: {"description": "Mensaje enviado"},
        400: {"description": "Mensaje vacío"},
        401: {"description": "Usuario sin sesión activa"},
        403: {"description": "El usuario no es miembro de la sala"},
        404: {"description": "Sala no encontrada"},
    }
)
def enviar_mensaje(roomname: str, body: MensajeRequest):
    verificar_sesion(body.username)
    verificar_sala(roomname)
    if body.username not in salas[roomname]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"'{body.username}' no es miembro de '{roomname}'")
    entrada = {
        "tipo": "EVT_MSG",
        "sala": roomname,
        "usuario": body.username,
        "texto": body.text,
    }
    mensajes[roomname].append(entrada)
    return {"mensaje": "Mensaje enviado correctamente", "entrada": entrada}


@app.get(
    "/rooms/{roomname}/messages",
    summary="Obtener mensajes de una sala",
    description=(
        "Devuelve los mensajes nuevos de la sala desde la última consulta del usuario (polling). "
        "Si se omite el parámetro username, devuelve todos los mensajes. "
        "Equivalente a getMessages del protocolo RMI."
    ),
    tags=["Mensajes"],
    responses={
        200: {"description": "Lista de mensajes"},
        404: {"description": "Sala no encontrada"},
    }
)
def obtener_mensajes(roomname: str, username: Optional[str] = None, todos: bool = False):
    verificar_sala(roomname)
    todos_los_msgs = mensajes[roomname]

    if todos or username is None:
        return {"sala": roomname, "mensajes": todos_los_msgs, "total": len(todos_los_msgs)}

    key = f"{username}:{roomname}"
    desde = ultimo_leido.get(key, 0)
    nuevos = todos_los_msgs[desde:]
    ultimo_leido[key] = len(todos_los_msgs)
    return {"sala": roomname, "mensajes": nuevos, "total_nuevos": len(nuevos)}
