import socket
import threading
import sys

# --- CONFIGURACIÓN DEL CLIENTE ---
HOST = '127.0.0.1'  # Pon aquí la IP de tu compañero cuando probéis en red
PORT = 8080

def recibir_mensajes(cliente):
    """
    Hilo dedicado a escuchar al servidor de forma continua.
    Procesa el buffer buscando CRLF (\r\n) y traduce los mensajes ABNF.
    """
    buffer = ""
    try:
        while True:
            data = cliente.recv(1024)
            if not data:
                print("\n[!] El servidor ha cerrado la conexión.")
                break
            
            buffer += data.decode('utf-8')
            
            # Buscamos mensajes delimitados por \r\n
            while '\r\n' in buffer:
                mensaje, buffer = buffer.split('\r\n', 1)
                mensaje = mensaje.strip()
                
                if mensaje:
                    procesar_respuesta(mensaje)
                    
    except ConnectionAbortedError:
        print("\n[!] Conexión abortada localmente.")
    except ConnectionResetError:
        print("\n[!] Se ha perdido la conexión con el servidor.")
    finally:
        # Forzamos la salida del programa si el servidor se cae
        print("Pulsa Enter para salir...")

def procesar_respuesta(mensaje):
    """
    Traduce el protocolo estricto ABNF a mensajes amigables para el usuario.
    """
    partes = mensaje.split(' ', 2)
    tipo = partes[0]

    # --- RESPUESTAS DE ÉXITO ---
    if tipo == "RES_OK":
        comando = partes[1] if len(partes) > 1 else ""
        if comando == "LOGIN" or comando == "REGISTER":
            print("[✓] ¡Autenticación completada con éxito!")
        elif comando == "ROOM_CREATE":
            print("[✓] Sala creada correctamente.")
        elif comando == "ROOM_JOIN":
            print("[✓] Te has unido a la sala.")
        elif comando == "MSG_SEND":
            pass # No imprimimos nada para no ensuciar el chat
        elif comando == "ROOM_LEAVE":
            print("[✓] Has abandonado la sala.")
        elif comando == "ROOM_DELETE":
            print("[✓] Sala eliminada.")

    # --- RESPUESTAS DE ERROR ---
    elif tipo == "RES_ERR":
        codigo = partes[1]
        texto = partes[2] if len(partes) > 2 else "Error desconocido"
        print(f"[ERROR {codigo}] -> {texto}")

    # --- EVENTOS DE MENSAJE (El chat en sí) ---
    elif tipo == "EVT_MSG":
        # Formato: EVT_MSG roomname username text
        partes_msg = mensaje.split(' ', 3)
        if len(partes_msg) == 4:
            sala = partes_msg[1]
            usuario = partes_msg[2]
            texto = partes_msg[3]
            print(f"\n[{sala}] {usuario}: {texto}")

    # --- EVENTOS DE ACTUALIZACIÓN DE SALA ---
    elif tipo == "EVT_ROOM_UPDATE":
        # Formato: EVT_ROOM_UPDATE roomname action username
        partes_evt = mensaje.split(' ', 3)
        if len(partes_evt) == 4:
            sala = partes_evt[1]
            accion = partes_evt[2]
            usuario = partes_evt[3]
            if accion == "JOIN":
                print(f"[!] {usuario} se ha unido a la sala {sala}.")
            elif accion == "LEAVE":
                print(f"[!] {usuario} ha abandonado la sala {sala}.")

    # --- LISTADO DE USUARIOS ---
    elif tipo == "RES_USER_LIST":
        # Formato: RES_USER_LIST roomname user1 user2...
        partes_list = mensaje.split(' ', 2)
        if len(partes_list) == 3:
            sala = partes_list[1]
            usuarios = partes_list[2].split(' ')
            print(f"[-] Usuarios en {sala}: {', '.join(usuarios)}")
        else:
            print(f"[-] La sala está vacía.")
            
    else:
        print(f"[RAW] {mensaje}")


def iniciar_cliente():
    cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    try:
        cliente.connect((HOST, PORT))
        print(f"[*] Conectado al servidor {HOST}:{PORT}")
        print("="*45)
        print(" COMANDOS DEL PROTOCOLO (Escríbelos tal cual)")
        print("="*45)
        print(" LOGIN <usuario> <pass>    (Ej: LOGIN admin admin)")
        print(" REGISTER <usuario> <pass> (Ej: REGISTER pepe 1234)")
        print(" ROOM_CREATE <sala>        (Ej: ROOM_CREATE general)")
        print(" ROOM_JOIN <sala>          (Ej: ROOM_JOIN general)")
        print(" MSG_SEND <sala> <texto>   (Ej: MSG_SEND general Hola!)")
        print(" ROOM_LEAVE <sala>")
        print(" GET_USERS <sala>")
        print(" ROOM_DELETE <sala>        (Solo admin)")
        print(" SHUTDOWN                  (Solo admin)")
        print("---------------------------------------------")
        print(" -> Escribe 'cerrar' o 'QUIT' para salir.\n")
        
        hilo_recepcion = threading.Thread(target=recibir_mensajes, args=(cliente,))
        hilo_recepcion.daemon = True
        hilo_recepcion.start()
        
        while True:
            mensaje = input("")
            
            # Opción para salir limpiamente
            if mensaje.strip().lower() == 'cerrar' or mensaje.strip().upper() == 'QUIT':
                print("[*] Desconectando...")
                cliente.sendall(b"QUIT\r\n")
                break
                
            if mensaje:
                # ¡VITAL! Añadimos \r\n al final de todo lo que enviamos
                mensaje_con_crlf = mensaje + "\r\n"
                cliente.sendall(mensaje_con_crlf.encode('utf-8'))
                
    except ConnectionRefusedError:
        print("[-] Error: No se pudo conectar. ¿Está el servidor encendido y la IP es correcta?")
    except KeyboardInterrupt:
        print("\n[*] Saliendo de forma forzosa...")
    finally:
        cliente.close()
        sys.exit(0)

if __name__ == "__main__":
    iniciar_cliente()