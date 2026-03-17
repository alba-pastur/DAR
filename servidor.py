import socket
import threading
import os

# --- CONFIGURACIÓN DEL SERVIDOR ---
HOST = '0.0.0.0'
PORT = 8080

# --- ESTADO GLOBAL DEL SERVIDOR ---
# Diccionario de base de datos de usuarios (Usuario -> Contraseña)
# Ya metemos al admin por defecto para cumplir con tu requisito
usuarios_registrados = {"admin": "admin"} 

# Diccionario de conexiones activas (Socket -> Usuario)
usuarios_conectados = {}  

# Diccionario de salas (Nombre de sala -> Lista de sockets)
salas = {} 

estado_lock = threading.Lock() 


def manejar_cliente(conn, addr):
    print(f"[+] Nueva conexión desde {addr}")
    buffer = ""
    
    try:
        while True:
            data = conn.recv(1024)
            if not data:
                break 
            
            buffer += data.decode('utf-8')
            
            # EL ABNF EXIGE CRLF (\r\n) COMO DELIMITADOR
            while '\r\n' in buffer:
                mensaje, buffer = buffer.split('\r\n', 1)
                mensaje = mensaje.strip()
                
                if mensaje:
                    procesar_mensaje(conn, mensaje)

    except ConnectionResetError:
        print(f"[-] Conexión perdida inesperadamente con {addr}")
    finally:
        desconectar_cliente(conn)


def procesar_mensaje(conn, mensaje):
    # Separamos en máximo 3 partes (COMANDO, ARG1, RESTO_DEL_TEXTO)
    partes = mensaje.split(' ', 2) 
    comando = partes[0].upper()

    with estado_lock:
        
        # -----------------------------------------------------------
        # 1. REGISTRO Y LOGIN (Requisitos de tu ABNF)
        # -----------------------------------------------------------
        if comando == "REGISTER" and len(partes) == 3:
            username = partes[1]
            password = partes[2]
            
            if username in usuarios_registrados:
                conn.sendall(b"RES_ERR 409 El usuario ya existe\r\n")
            else:
                usuarios_registrados[username] = password
                conn.sendall(b"RES_OK REGISTER\r\n")

        elif comando == "LOGIN" and len(partes) == 3:
            username = partes[1]
            password = partes[2]
            
            if username not in usuarios_registrados:
                conn.sendall(b"RES_ERR 404 Usuario no encontrado\r\n")
            elif usuarios_registrados[username] != password:
                conn.sendall(b"RES_ERR 401 Contrasena incorrecta\r\n")
            elif username in usuarios_conectados.values():
                conn.sendall(b"RES_ERR 403 El usuario ya esta conectado\r\n")
            else:
                usuarios_conectados[conn] = username
                conn.sendall(b"RES_OK LOGIN\r\n")

        # -----------------------------------------------------------
        # PROTECCIÓN: Si no estás logueado, no pasas de aquí
        # -----------------------------------------------------------
        elif conn not in usuarios_conectados:
            if comando == "QUIT":
                conn.sendall(b"RES_OK QUIT\r\n")
                # Se cerrará en el finally del hilo
            else:
                conn.sendall(b"RES_ERR 401 No autenticado. Usa LOGIN o REGISTER primero\r\n")
            return

        # -----------------------------------------------------------
        # 2. GESTIÓN DE SALAS Y MENSAJES (El núcleo del ABNF)
        # -----------------------------------------------------------
        elif comando == "ROOM_CREATE" and len(partes) >= 2:
            roomname = partes[1]
            if roomname in salas:
                conn.sendall(b"RES_ERR 409 La sala ya existe\r\n")
            else:
                salas[roomname] = []
                conn.sendall(b"RES_OK ROOM_CREATE\r\n")

        elif comando == "ROOM_DELETE" and len(partes) >= 2:
            roomname = partes[1]
            # Solo permitimos borrar salas al admin
            if usuarios_conectados[conn] == "admin":
                if roomname in salas:
                    # Echamos a todos de la sala antes de borrarla
                    notificar_sala(roomname, f"EVT_ROOM_UPDATE {roomname} LEAVE ALL\r\n")
                    del salas[roomname]
                    conn.sendall(b"RES_OK ROOM_DELETE\r\n")
                else:
                    conn.sendall(b"RES_ERR 404 La sala no existe\r\n")
            else:
                conn.sendall(b"RES_ERR 403 Solo el administrador puede borrar salas\r\n")

        elif comando == "ROOM_JOIN" and len(partes) >= 2:
            roomname = partes[1]
            if roomname not in salas:
                conn.sendall(b"RES_ERR 404 La sala no existe\r\n")
            else:
                if conn not in salas[roomname]:
                    salas[roomname].append(conn)
                    conn.sendall(b"RES_OK ROOM_JOIN\r\n")
                    nick = usuarios_conectados[conn]
                    notificar_sala(roomname, f"EVT_ROOM_UPDATE {roomname} JOIN {nick}\r\n", excluyendo=conn)
                else:
                    conn.sendall(b"RES_ERR 400 Ya estas en esta sala\r\n")

        elif comando == "MSG_SEND" and len(partes) == 3:
            roomname = partes[1]
            texto = partes[2]
            if roomname in salas and conn in salas[roomname]:
                nick = usuarios_conectados[conn]
                # ABNF: evt-msg = "EVT_MSG" SP roomname SP username SP text
                mensaje_evt = f"EVT_MSG {roomname} {nick} {texto}\r\n"
                notificar_sala(roomname, mensaje_evt, excluyendo=conn)
                conn.sendall(b"RES_OK MSG_SEND\r\n")
            else:
                conn.sendall(b"RES_ERR 403 No estas en la sala o no existe\r\n")

        elif comando == "ROOM_LEAVE" and len(partes) >= 2:
            roomname = partes[1]
            if roomname in salas and conn in salas[roomname]:
                salas[roomname].remove(conn)
                conn.sendall(b"RES_OK ROOM_LEAVE\r\n")
                nick = usuarios_conectados[conn]
                notificar_sala(roomname, f"EVT_ROOM_UPDATE {roomname} LEAVE {nick}\r\n")
            else:
                conn.sendall(b"RES_ERR 403 No estas en esta sala\r\n")

        elif comando == "GET_USERS" and len(partes) >= 2:
            roomname = partes[1]
            if roomname in salas:
                usuarios_en_sala = [usuarios_conectados[c] for c in salas[roomname]]
                lista_str = " ".join(usuarios_en_sala) # Separado por espacios según ABNF
                respuesta = f"RES_USER_LIST {roomname} {lista_str}\r\n"
                conn.sendall(respuesta.encode('utf-8'))
                conn.sendall(b"RES_OK GET_USERS\r\n")
            else:
                conn.sendall(b"RES_ERR 404 La sala no existe\r\n")

        elif comando == "QUIT":
            conn.sendall(b"RES_OK QUIT\r\n")
            # Forzamos desconexión llamando a la función
            desconectar_cliente(conn)

        elif comando == "SHUTDOWN":
            if usuarios_conectados.get(conn) == "admin":
                print("\n[*] El admin ha ordenado apagar el servidor de forma remota.")
                os._exit(0)
            else:
                conn.sendall(b"RES_ERR 403 No tienes permisos\r\n")

        else:
            conn.sendall(b"RES_ERR 400 Comando invalido o parametros incorrectos\r\n")


def notificar_sala(nombre_sala, mensaje, excluyendo=None):
    for socket_cliente in salas.get(nombre_sala, []):
        if socket_cliente != excluyendo:
            try:
                socket_cliente.sendall(mensaje.encode('utf-8'))
            except:
                pass


def desconectar_cliente(conn):
    with estado_lock:
        nick = usuarios_conectados.get(conn, None)
        
        for roomname, lista_sockets in salas.items():
            if conn in lista_sockets:
                lista_sockets.remove(conn)
                if nick:
                    notificar_sala(roomname, f"EVT_ROOM_UPDATE {roomname} LEAVE {nick}\r\n")
        
        if conn in usuarios_conectados:
            del usuarios_conectados[conn]
            
        try:
            conn.close()
        except:
            pass
        if nick:
            print(f"[-] {nick} desconectado.")


# --- CONSOLA PARA APAGAR EL SERVIDOR DESDE LA PANTALLA ---
def consola_servidor(servidor):
    print("\n[INFO] Escribe 'cerrar' en cualquier momento para apagar el servidor.\n")
    while True:
        comando = input()
        if comando.strip().lower() == 'cerrar':
            print("\n[*] Apagando el servidor localmente...")
            try:
                servidor.close()
            except:
                pass
            os._exit(0)


def iniciar_servidor():
    servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    servidor.bind((HOST, PORT))
    servidor.listen()
    print(f"[*] Servidor ABNF escuchando en el puerto {PORT}...")
    
    hilo_teclado = threading.Thread(target=consola_servidor, args=(servidor,))
    hilo_teclado.daemon = True
    hilo_teclado.start()
    
    try:
        while True:
            conn, addr = servidor.accept()
            hilo = threading.Thread(target=manejar_cliente, args=(conn, addr))
            hilo.daemon = True
            hilo.start()
            
    except OSError:
        pass
    except KeyboardInterrupt:
        print("\n[*] Apagando servidor mediante teclado (Ctrl+C)...")
    finally:
        servidor.close()

if __name__ == "__main__":
    iniciar_servidor()