# DAR
PRÁCTICA DAR

---


### Inicializar un proyecto nuevo desde cero

1. **Entra en la carpeta:** `cd "ruta\de\tu\carpeta"`
2. **Inicializa:** `git init`
3. **Conecta con GitHub:** `git remote add origin https://github.com/TU_USUARIO/NOMBRE_REPO.git`
4. **Crea la rama principal:** `git branch -M main`

### Añadir, confirmar y subir archivos iniciales
```bash
git add .
git commit -m "Primer commit"
git push -u origin main

```
### Sactualizar el PC
```bash
git pull origin main --rebase

```
### Al terminar de programar o modificar archivos
**1. Añadir todo lo nuevo:**

```bash
git add .

```

**2. Guardar el "paquete":**

```bash
git commit -m "Descripción de lo que has hecho"

```

**3. Subir a la nube:**

```bash
git push origin main

```

---

# Práctica: Protocolo de Chat Multiusuario con Salas

Este repositorio contiene la especificación formal y la implementación de un protocolo de chat multiusuario en arquitectura Cliente-Servidor mediante Sockets TCP, cumpliendo con los requisitos de la práctica.

---

## 1. Especificación ABNF del Protocolo

El protocolo utiliza `\r\n` (CRLF) como delimitador de mensajes.

```abnf
message = (client-msg / server-msg) CRLF

; MENSAJES DEL CLIENTE
client-msg = cmd-register / cmd-login / cmd-create / cmd-delete / cmd-join / cmd-leave / cmd-send / cmd-list / cmd-quit / cmd-shutdown
cmd-register = "REGISTER" SP username SP password
cmd-login    = "LOGIN" SP username SP password
cmd-create   = "ROOM_CREATE" SP roomname
cmd-delete   = "ROOM_DELETE" SP roomname
cmd-join     = "ROOM_JOIN" SP roomname
cmd-leave    = "ROOM_LEAVE" SP roomname
cmd-send     = "MSG_SEND" SP roomname SP text
cmd-list     = "GET_USERS" SP roomname
cmd-quit     = "QUIT"
cmd-shutdown = "SHUTDOWN"

; MENSAJES DEL SERVIDOR
server-msg = res-ok / res-err / evt-msg / evt-update / res-list
res-ok     = "RES_OK" SP command-name
res-err    = "RES_ERR" SP error-code SP text
evt-msg    = "EVT_MSG" SP roomname SP username SP text
evt-update = "EVT_ROOM_UPDATE" SP roomname SP action SP username
res-list   = "RES_USER_LIST" SP roomname *(SP username)

; TIPOS DE DATOS
username     = 3*16(ALPHA / DIGIT)
password     = 4*32(VCHAR)
roomname     = 3*20(ALPHA / DIGIT / "-" / "_")
text         = 1*(VCHAR / SP / HTAB)
action       = "JOIN" / "LEAVE"
error-code   = 3DIGIT
command-name = "REGISTER" / "LOGIN" / "ROOM_CREATE" / "ROOM_DELETE" / "ROOM_JOIN" / "ROOM_LEAVE" / "MSG_SEND" / "GET_USERS" / "QUIT" / "SHUTDOWN"

SP   = %x20
HTAB = %x09
CRLF = %x0D %x0A
ALPHA = %x41-5A / %x61-7A
DIGIT = %x30-39
VCHAR = %x21-7E


