package chat;

import java.rmi.Naming;
import java.util.List;
import java.util.Scanner;
import java.util.concurrent.Executors;
import java.util.concurrent.ScheduledExecutorService;
import java.util.concurrent.TimeUnit;

public class Cliente {

    private static ChatInterfaz chat;
    private static String usuarioActual = null;
    private static String salaActual = null;
    private static final Scanner sc = new Scanner(System.in);
    private static ScheduledExecutorService poller;

    public static void main(String[] args) {

        String host = "localhost";
        if (args.length > 0) host = args[0];

        try {
            chat = (ChatInterfaz) Naming.lookup("rmi://" + host + ":1099/chat");
            System.out.println("Conectado al servidor RMI en " + host);
        } catch (Exception e) {
            System.err.println("Error al conectar: " + e.getMessage());
            return;
        }

        mostrarMenuPrincipal();
    }

    private static void mostrarMenuPrincipal() {
        while (true) {
            System.out.println("\n=== CHAT RMI ===");
            if (usuarioActual == null) {
                System.out.println("1. Registrarse");
                System.out.println("2. Iniciar sesión");
                System.out.println("0. Salir");
            } else {
                System.out.println("Usuario: " + usuarioActual);
                System.out.println("3. Crear sala");
                System.out.println("4. Eliminar sala");
                System.out.println("5. Unirse a sala");
                System.out.println("6. Abandonar sala");
                System.out.println("7. Ver usuarios en sala");
                System.out.println("8. Enviar mensaje");
                System.out.println("9. Ver mensajes nuevos");
                System.out.println("0. Desconectarse");
            }
            System.out.print("> ");
            String opcion = sc.nextLine().trim();

            try {
                switch (opcion) {
                    case "1" -> registrar();
                    case "2" -> login();
                    case "3" -> crearSala();
                    case "4" -> eliminarSala();
                    case "5" -> unirseASala();
                    case "6" -> abandonarSala();
                    case "7" -> verUsuarios();
                    case "8" -> enviarMensaje();
                    case "9" -> verMensajes();
                    case "0" -> {
                        salir();
                        return;
                    }
                    default -> System.out.println("Opción no válida.");
                }
            } catch (java.rmi.RemoteException e) {
                System.err.println("Error de red: " + e.getMessage());
            }
        }
    }

    private static void registrar() throws java.rmi.RemoteException {
        System.out.print("Usuario (3-16 chars): ");
        String user = sc.nextLine().trim();
        System.out.print("Contraseña (4-32 chars): ");
        String pass = sc.nextLine().trim();
        System.out.println(chat.register(user, pass));
    }

    private static void login() throws java.rmi.RemoteException {
        System.out.print("Usuario: ");
        String user = sc.nextLine().trim();
        System.out.print("Contraseña: ");
        String pass = sc.nextLine().trim();
        String resp = chat.login(user, pass);
        System.out.println(resp);
        if (resp.startsWith("RES_OK")) {
            usuarioActual = user;
        }
    }

    private static void crearSala() throws java.rmi.RemoteException {
        System.out.print("Nombre de sala: ");
        String sala = sc.nextLine().trim();
        System.out.println(chat.createRoom(usuarioActual, sala));
    }

    private static void eliminarSala() throws java.rmi.RemoteException {
        System.out.print("Nombre de sala a eliminar: ");
        String sala = sc.nextLine().trim();
        System.out.println(chat.deleteRoom(usuarioActual, sala));
    }

    private static void unirseASala() throws java.rmi.RemoteException {
        System.out.print("Nombre de sala: ");
        String sala = sc.nextLine().trim();
        String resp = chat.joinRoom(usuarioActual, sala);
        System.out.println(resp);
        if (resp.startsWith("RES_OK")) {
            salaActual = sala;
        }
    }

    private static void abandonarSala() throws java.rmi.RemoteException {
        System.out.print("Nombre de sala: ");
        String sala = sc.nextLine().trim();
        String resp = chat.leaveRoom(usuarioActual, sala);
        System.out.println(resp);
        if (resp.startsWith("RES_OK") && sala.equals(salaActual)) {
            salaActual = null;
        }
    }

    private static void verUsuarios() throws java.rmi.RemoteException {
        System.out.print("Nombre de sala: ");
        String sala = sc.nextLine().trim();
        List<String> lista = chat.getUsers(sala);
        lista.forEach(System.out::println);
    }

    private static void enviarMensaje() throws java.rmi.RemoteException {
        System.out.print("Sala: ");
        String sala = sc.nextLine().trim();
        System.out.print("Mensaje: ");
        String texto = sc.nextLine().trim();
        System.out.println(chat.sendMessage(usuarioActual, sala, texto));
    }

    private static void verMensajes() throws java.rmi.RemoteException {
        System.out.print("Sala: ");
        String sala = sc.nextLine().trim();
        List<String> msgs = chat.getMessages(usuarioActual, sala);
        if (msgs.isEmpty()) {
            System.out.println("(Sin mensajes nuevos)");
        } else {
            msgs.forEach(System.out::println);
        }
    }

    private static void salir() throws java.rmi.RemoteException {
        if (usuarioActual != null) {
            System.out.println(chat.quit(usuarioActual));
            usuarioActual = null;
        }
        System.out.println("Desconectado.");
    }
}
