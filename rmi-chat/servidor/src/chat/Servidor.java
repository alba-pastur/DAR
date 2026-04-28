package chat;

import java.rmi.registry.LocateRegistry;
import java.rmi.registry.Registry;

public class Servidor {

    public static void main(String[] args) {

        int puerto = 1099;

        try {
            LocateRegistry.createRegistry(puerto);
            System.out.println("Registro RMI iniciado en el puerto " + puerto);
        } catch (Exception e) {
            System.err.println("Aviso al crear registro (puede que ya exista): " + e.getMessage());
        }

        try {
            ChatImplement chat = new ChatImplement();
            Registry registry = LocateRegistry.getRegistry(puerto);
            registry.rebind("chat", chat);
            System.out.println("Servidor de chat listo. Objeto registrado como 'chat'.");
            System.out.println("Esperando clientes...");
        } catch (Exception e) {
            System.err.println("Error fatal en el servidor: " + e.getMessage());
            e.printStackTrace();
        }
    }
}
