package chat;

import java.rmi.RemoteException;
import java.rmi.server.UnicastRemoteObject;
import java.util.*;
import java.util.concurrent.ConcurrentHashMap;

public class ChatImplement extends UnicastRemoteObject implements ChatInterfaz {

    // Estado compartido del servidor (thread-safe)
    private final Map<String, String> usuarios = new ConcurrentHashMap<>();          // username -> password
    private final Set<String> sesionesActivas = Collections.synchronizedSet(new HashSet<>());
    private final Map<String, Set<String>> salas = new ConcurrentHashMap<>();        // sala -> usuarios
    private final Map<String, List<String>> mensajes = new ConcurrentHashMap<>();    // sala -> mensajes
    private final Map<String, Integer> ultimoMensaje = new ConcurrentHashMap<>();    // username:sala -> último índice leído

    public ChatImplement() throws RemoteException {
        super();
    }

    // -------- GESTIÓN DE USUARIOS --------

    @Override
    public synchronized String register(String username, String password) throws RemoteException {
        if (!username.matches("[A-Za-z0-9]{3,16}"))
            return "RES_ERR 400 Usuario inválido (3-16 caracteres alfanuméricos)";
        if (!password.matches("[\\x21-\\x7E]{4,32}"))
            return "RES_ERR 400 Contraseña inválida (4-32 caracteres)";
        if (usuarios.containsKey(username))
            return "RES_ERR 409 Usuario ya registrado";
        usuarios.put(username, password);
        System.out.println("[REGISTER] " + username);
        return "RES_OK REGISTER";
    }

    @Override
    public synchronized String login(String username, String password) throws RemoteException {
        if (!usuarios.containsKey(username))
            return "RES_ERR 404 Usuario no encontrado";
        if (!usuarios.get(username).equals(password))
            return "RES_ERR 401 Contraseña incorrecta";
        if (sesionesActivas.contains(username))
            return "RES_ERR 409 Usuario ya conectado";
        sesionesActivas.add(username);
        System.out.println("[LOGIN] " + username);
        return "RES_OK LOGIN";
    }

    @Override
    public synchronized String quit(String username) throws RemoteException {
        sesionesActivas.remove(username);
        // Sacar al usuario de todas las salas
        for (Map.Entry<String, Set<String>> entry : salas.entrySet()) {
            if (entry.getValue().remove(username)) {
                mensajes.get(entry.getKey()).add("EVT_ROOM_UPDATE " + entry.getKey() + " LEAVE " + username);
            }
        }
        System.out.println("[QUIT] " + username);
        return "RES_OK QUIT";
    }

    // -------- GESTIÓN DE SALAS --------

    @Override
    public synchronized String createRoom(String username, String roomname) throws RemoteException {
        if (!sesionesActivas.contains(username))
            return "RES_ERR 401 No autenticado";
        if (!roomname.matches("[A-Za-z0-9\\-_]{3,20}"))
            return "RES_ERR 400 Nombre de sala inválido";
        if (salas.containsKey(roomname))
            return "RES_ERR 409 Sala ya existe";
        salas.put(roomname, Collections.synchronizedSet(new HashSet<>()));
        mensajes.put(roomname, Collections.synchronizedList(new ArrayList<>()));
        System.out.println("[ROOM_CREATE] " + roomname + " por " + username);
        return "RES_OK ROOM_CREATE";
    }

    @Override
    public synchronized String deleteRoom(String username, String roomname) throws RemoteException {
        if (!sesionesActivas.contains(username))
            return "RES_ERR 401 No autenticado";
        if (!salas.containsKey(roomname))
            return "RES_ERR 404 Sala no encontrada";
        salas.remove(roomname);
        mensajes.remove(roomname);
        System.out.println("[ROOM_DELETE] " + roomname + " por " + username);
        return "RES_OK ROOM_DELETE";
    }

    @Override
    public synchronized String joinRoom(String username, String roomname) throws RemoteException {
        if (!sesionesActivas.contains(username))
            return "RES_ERR 401 No autenticado";
        if (!salas.containsKey(roomname))
            return "RES_ERR 404 Sala no encontrada";
        salas.get(roomname).add(username);
        mensajes.get(roomname).add("EVT_ROOM_UPDATE " + roomname + " JOIN " + username);
        ultimoMensaje.put(username + ":" + roomname, mensajes.get(roomname).size());
        System.out.println("[ROOM_JOIN] " + username + " -> " + roomname);
        return "RES_OK ROOM_JOIN";
    }

    @Override
    public synchronized String leaveRoom(String username, String roomname) throws RemoteException {
        if (!sesionesActivas.contains(username))
            return "RES_ERR 401 No autenticado";
        if (!salas.containsKey(roomname))
            return "RES_ERR 404 Sala no encontrada";
        salas.get(roomname).remove(username);
        mensajes.get(roomname).add("EVT_ROOM_UPDATE " + roomname + " LEAVE " + username);
        System.out.println("[ROOM_LEAVE] " + username + " <- " + roomname);
        return "RES_OK ROOM_LEAVE";
    }

    // -------- MENSAJERÍA --------

    @Override
    public String sendMessage(String username, String roomname, String text) throws RemoteException {
        if (!sesionesActivas.contains(username))
            return "RES_ERR 401 No autenticado";
        if (!salas.containsKey(roomname))
            return "RES_ERR 404 Sala no encontrada";
        if (!salas.get(roomname).contains(username))
            return "RES_ERR 403 No estás en esta sala";
        if (text == null || text.trim().isEmpty())
            return "RES_ERR 400 Mensaje vacío";
        mensajes.get(roomname).add("EVT_MSG " + roomname + " " + username + " " + text);
        return "RES_OK MSG_SEND";
    }

    @Override
    public List<String> getMessages(String username, String roomname) throws RemoteException {
        if (!salas.containsKey(roomname))
            return List.of("RES_ERR 404 Sala no encontrada");
        String key = username + ":" + roomname;
        int desde = ultimoMensaje.getOrDefault(key, 0);
        List<String> todos = mensajes.get(roomname);
        List<String> nuevos = new ArrayList<>(todos.subList(desde, todos.size()));
        ultimoMensaje.put(key, todos.size());
        return nuevos;
    }

    @Override
    public List<String> getUsers(String roomname) throws RemoteException {
        if (!salas.containsKey(roomname))
            return List.of("RES_ERR 404 Sala no encontrada");
        List<String> lista = new ArrayList<>(salas.get(roomname));
        List<String> resultado = new ArrayList<>();
        resultado.add("RES_USER_LIST " + roomname + " " + String.join(" ", lista));
        return resultado;
    }
}
