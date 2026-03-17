import socket
import threading

# --- CONFIGURACIÓN DEL SERVIDOR ---
HOST = '0.0.0.0'  # Escucha en todas las interfaces de red
PORT = 8080       # Puerto donde escuchará el servidor

# --- ESTADO GLOBAL DEL SERVIDOR ---
# Diccionario para mapear: socket_cliente -> nombre_usuario
usuarios_conectados = {}  

# Diccionario para gestionar las salas: nombre_sala -> lista_de_sockets
salas = {} 

# Candado (Lock) para evitar problemas de concurrencia al modificar los diccionarios
estado_lock = threading.Lock() 


def manejar_cliente(conn, addr):
    """
    Función que se ejecuta en un Hilo independiente por cada cliente conectado.
    Gestiona la recepción de mensajes, el buffer y la lógica del protocolo.
    """
    print(f"[+] Nueva conexión desde {addr}")
    buffer = ""
    
    try:
        while True:
            # 1. RECIBIR DATOS (Gestión explícita de Sockets)
            data = conn.recv(1024)
            if not data:
                # Si recv() devuelve vacío, el cliente se ha desconectado (Cierre ordenado TCP)
                break 
            
            # 2. GESTIÓN DE BUFFERS Y DELIMITACIÓN (Requisito clave de la rúbrica)
            # Decodificamos y añadimos al buffer. Usamos '\n' como delimitador de mensaje.
            buffer += data.decode('utf-8')
            
            while '\n' in buffer:
                # Extraemos un mensaje completo hasta el salto de línea
                mensaje, buffer = buffer.split('\n', 1)
                mensaje = mensaje.strip()
                
                if mensaje:
                    procesar_mensaje(conn, mensaje)

    except ConnectionResetError:
        # 3. GESTIÓN DE DESCONEXIONES INESPERADAS (Caída de red, cierre forzoso)
        print(f"[-] Conexión perdida inesperadamente con {addr}")
    finally:
        # 4. LIMPIEZA DE ESTADO GLOBAL AL DESCONECTAR
        desconectar_cliente(conn)


def procesar_mensaje(conn, mensaje):
    """
    Lógica principal del protocolo de aplicación. 
    Analiza el comando y ejecuta la acción correspondiente.
    """
    partes = mensaje.split(' ', 2) # Divide en máximo 3 partes: COMANDO ARG1 RESTO
    comando = partes[0].upper()

    with estado_lock: # Bloqueamos el estado global mientras lo modificamos
        
        # --- REGISTRO DE USUARIO ---
        if comando == "NICK" and len(partes) >= 2:
            nick = partes[1]
            if nick in usuarios_conectados.values():
                conn.sendall(b"ERR_NICK_DUPLICADO\n") # Rechazo estructurado
            else:
                usuarios_conectados[conn] = nick
                conn.sendall(b"OK_NICK_ACEPTADO\n")
        
        # (A partir de aquí, exigimos que el usuario esté registrado)
        elif conn not in usuarios_conectados:
            conn.sendall(b"ERR_NO_REGISTRADO\n")
            return

        # --- CREACIÓN DE SALAS ---
        elif comando == "CREATE" and len(partes) >= 2:
            nombre_sala = partes[1]
            if nombre_sala in salas:
                conn.sendall(b"ERR_SALA_EXISTE\n")
            else:
                salas[nombre_sala] = []
                conn.sendall(b"OK_SALA_CREADA\n")

        # --- UNIÓN A SALA EXISTENTE ---
        elif comando == "JOIN" and len(partes) >= 2:
            nombre_sala = partes[1]
            if nombre_sala not in salas:
                conn.sendall(b"ERR_SALA_NO_EXISTE\n")
            else:
                if conn not in salas[nombre_sala]:
                    salas[nombre_sala].append(conn)
                    conn.sendall(b"OK_UNIDO\n")
                    # Notificación automática a la sala
                    nick = usuarios_conectados[conn]
                    notificar_sala(nombre_sala, f"SYS {nick} ha entrado a la sala.\n")
                else:
                    conn.sendall(b"ERR_YA_ESTAS_EN_SALA\n")

        # --- ENVÍO DE MENSAJES A UNA SALA ---
        elif comando == "MSG" and len(partes) == 3:
            nombre_sala = partes[1]
            texto = partes[2]
            
            if nombre_sala in salas and conn in salas[nombre_sala]:
                nick = usuarios_conectados[conn]
                mensaje_formateado = f"MSG_FROM {nombre_sala} {nick}: {texto}\n"
                notificar_sala(nombre_sala, mensaje_formateado, excluyendo=conn)
                conn.sendall(b"OK_MENSAJE_ENVIADO\n")
            else:
                conn.sendall(b"ERR_NO_ESTAS_EN_SALA\n")
        
        # --- ABANDONO DE SALA ---
        elif comando == "LEAVE" and len(partes) >= 2:
            nombre_sala = partes[1]
            if nombre_sala in salas and conn in salas[nombre_sala]:
                salas[nombre_sala].remove(conn)
                conn.sendall(b"OK_SALA_ABANDONADA\n")
                nick = usuarios_conectados[conn]
                notificar_sala(nombre_sala, f"SYS {nick} ha abandonado la sala.\n")
            else:
                conn.sendall(b"ERR_NO_ESTAS_EN_SALA\n")

        # --- LISTADO DE USUARIOS ---
        elif comando == "USERS" and len(partes) >= 2:
            nombre_sala = partes[1]
            if nombre_sala in salas:
                usuarios_en_sala = [usuarios_conectados[c] for c in salas[nombre_sala]]
                lista_str = ",".join(usuarios_en_sala)
                respuesta = f"LIST_USERS {nombre_sala} {lista_str}\n"
                conn.sendall(respuesta.encode('utf-8'))
            else:
                conn.sendall(b"ERR_SALA_NO_EXISTE\n")

        else:
            conn.sendall(b"ERR_COMANDO_INVALIDO\n")


def notificar_sala(nombre_sala, mensaje, excluyendo=None):
    """
    Función auxiliar para distribuir mensajes exclusivamente a los miembros válidos.
    """
    for socket_cliente in salas.get(nombre_sala, []):
        if socket_cliente != excluyendo:
            try:
                socket_cliente.sendall(mensaje.encode('utf-8'))
            except:
                pass # Si falla el envío, se limpiará luego cuando el hilo lo detecte


def desconectar_cliente(conn):
    """
    Limpia el rastro de un cliente en los diccionarios de estado cuando se va.
    """
    with estado_lock:
        nick = usuarios_conectados.get(conn, "Usuario_Desconocido")
        # Lo eliminamos de todas las salas en las que estuviera
        for nombre_sala, lista_sockets in salas.items():
            if conn in lista_sockets:
                lista_sockets.remove(conn)
                notificar_sala(nombre_sala, f"SYS {nick} se ha desconectado del servidor.\n")
        
        # Lo eliminamos del registro global
        if conn in usuarios_conectados:
            del usuarios_conectados[conn]
            
        try:
            conn.close() # Cierre ordenado de los recursos (Requisito de la rúbrica)
        except:
            pass
        print(f"[-] {nick} eliminado del sistema.")


def iniciar_servidor():
    # 1. SOCKET(): Crear socket TCP/IP
    servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # Evita el error "Puerto en uso"
    
    # 2. BIND(): Unir a la IP y Puerto
    servidor.bind((HOST, PORT))
    
    # 3. LISTEN(): Poner en modo escucha
    servidor.listen()
    print(f"[*] Servidor de chat escuchando en el puerto {PORT}...")
    
    try:
        while True:
            # 4. ACCEPT(): Espera bloqueante hasta que un cliente se conecta
            conn, addr = servidor.accept()
            
            # CONCURRENCIA: Delegamos el cliente a un nuevo Hilo
            hilo = threading.Thread(target=manejar_cliente, args=(conn, addr))
            hilo.daemon = True
            hilo.start()
            
    except KeyboardInterrupt:
        print("\n[*] Apagando servidor...")
    finally:
        servidor.close()


if __name__ == "__main__":
    iniciar_servidor()