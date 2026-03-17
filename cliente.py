import socket
import threading
import sys

# Configuración (debe coincidir con el servidor)
HOST = '172.17.110.8'
PORT = 8080

def recibir_mensajes(sock):
    """
    Este hilo se dedica ÚNICAMENTE a escuchar lo que llega del servidor
    y pintarlo en la pantalla.
    """
    try:
        while True:
            data = sock.recv(1024)
            if not data:
                print("\n[!] El servidor ha cerrado la conexión.")
                break
            # Imprimimos el mensaje del servidor
            print(f"\n[SERVIDOR] -> {data.decode('utf-8').strip()}")
    except Exception as e:
        print(f"\n[!] Error de conexión: {e}")
    finally:
        sock.close()
        sys.exit(0)

def iniciar_cliente():
    # 1. SOCKET(): Creamos el socket del cliente
    cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        # 2. CONNECT(): Llamamos a la puerta del servidor
        cliente.connect((HOST, PORT))
        print(f"[*] Conectado al servidor {HOST}:{PORT}")
        print("--- COMANDOS DISPONIBLES ---")
        print(" NICK <nombre>    -> Para registrarte")
        print(" CREATE <sala>    -> Para crear una sala")
        print(" JOIN <sala>      -> Para entrar a una sala")
        print(" MSG <sala> <txt> -> Para enviar un mensaje")
        print(" LEAVE <sala>     -> Para salir de la sala")
        print("----------------------------")

        # Lanzamos un hilo independiente para recibir mensajes sin bloquear el teclado
        hilo_recepcion = threading.Thread(target=recibir_mensajes, args=(cliente,))
        hilo_recepcion.daemon = True
        hilo_recepcion.start()

        # Bucle principal: Leer del teclado y enviar al servidor
        while True:
            mensaje = input("")
            if mensaje.upper() == 'QUIT':
                break

            if mensaje:
                # Añadimos el \n porque nuestro servidor exige ese delimitador
                mensaje_con_salto = mensaje + "\n"
                cliente.sendall(mensaje_con_salto.encode('utf-8'))

    except ConnectionRefusedError:
        print("[-] Error: No se pudo conectar. ¿Está el servidor encendido?")
    except KeyboardInterrupt:
        print("\n[*] Saliendo...")
    finally:
        cliente.close()

if __name__ == "__main__":
    iniciar_cliente()