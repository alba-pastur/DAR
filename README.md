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
### Actualizar el PC
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
CADA VEZ QUE QUERAMOS ACTUALIZAR ALGO:

**1. Descargamos lo último de GitHub**
```cmd
git pull origin main --no-edit
```

**2. Preparamos todos los archivos:**
```cmd
git add .
```

**3. Creamos el paquete: ejemplo: subimos una captura de wireshark**
```cmd
git commit -m "Añadida captura de tráfico .pcap demostrando el protocolo"
```

**4. Lo subimos todo**
```cmd
git push
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

```

---

### 2. Máquina de Estados del Servidor (Por Cliente)

```abnf
stateDiagram-v2
    [*] --> NO_AUTENTICADO : Conexión aceptada
    NO_AUTENTICADO --> NO_AUTENTICADO : REGISTER (Crea usuario)
    NO_AUTENTICADO --> AUTENTICADO : LOGIN (Credenciales OK)
    NO_AUTENTICADO --> [*] : QUIT / Desconexión
    
    AUTENTICADO --> AUTENTICADO : ROOM_CREATE
    AUTENTICADO --> EN_SALA : ROOM_JOIN
    AUTENTICADO --> [*] : QUIT / Desconexión
    
    EN_SALA --> EN_SALA : MSG_SEND / GET_USERS
    EN_SALA --> AUTENTICADO : ROOM_LEAVE
    EN_SALA --> [*] : QUIT / Desconexión

```
---
## 3.Diagrama de Secuencia (Flujo Nominal)

```abnf
sequenceDiagram
    participant C1 as Cliente 1 (Admin)
    participant S as Servidor
    participant C2 as Cliente 2 (Pepe)

    C1->>S: LOGIN admin admin\r\n
    S-->>C1: RES_OK LOGIN\r\n
    C1->>S: ROOM_CREATE general\r\n
    S-->>C1: RES_OK ROOM_CREATE\r\n
    C1->>S: ROOM_JOIN general\r\n
    S-->>C1: RES_OK ROOM_JOIN\r\n
    
    C2->>S: REGISTER pepe 1234\r\n
    S-->>C2: RES_OK REGISTER\r\n
    C2->>S: ROOM_JOIN general\r\n
    S-->>C1: EVT_ROOM_UPDATE general JOIN pepe\r\n
    S-->>C2: RES_OK ROOM_JOIN\r\n
    
    C2->>S: MSG_SEND general Hola jefe\r\n
    S-->>C1: EVT_MSG general pepe Hola jefe\r\n
    S-->>C2: RES_OK MSG_SEND\r\n
```
---

## 4. Gestión de Errores y Códigos de Respuesta
```abnf
Código,Significado,Escenario de disparo
400,Bad Request,"Operación no válida (ej. Unirse a una sala en la que ya estás, parámetros mal formados)."
401,Unauthorized,Contraseña incorrecta al hacer LOGIN o intento de usar comandos sin estar autenticado.
403,Forbidden,"Permisos insuficientes (ej. Borrar sala sin ser admin, enviar mensaje a sala donde no estás)."
404,Not Found,"Entidad inexistente (ej. Hacer LOGIN con usuario no registrado, unirse a sala borrada)."
409,Conflict,"Duplicidad (ej. Registrar usuario que ya existe, crear sala que ya existe)."




```


