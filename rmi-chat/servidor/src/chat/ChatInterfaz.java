package chat;

import java.rmi.Remote;
import java.rmi.RemoteException;
import java.util.List;

public interface ChatInterfaz extends Remote {

    // Gestión de usuarios
    String register(String username, String password) throws RemoteException;
    String login(String username, String password) throws RemoteException;
    String quit(String username) throws RemoteException;

    // Gestión de salas
    String createRoom(String username, String roomname) throws RemoteException;
    String deleteRoom(String username, String roomname) throws RemoteException;
    String joinRoom(String username, String roomname) throws RemoteException;
    String leaveRoom(String username, String roomname) throws RemoteException;

    // Mensajería
    String sendMessage(String username, String roomname, String text) throws RemoteException;
    List<String> getMessages(String username, String roomname) throws RemoteException;
    List<String> getUsers(String roomname) throws RemoteException;
}
