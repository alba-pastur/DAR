# Chat Multiusuario RMI - Java

## Estructura
```
rmi-chat/
├── servidor/src/chat/
│   ├── ChatInterfaz.java
│   ├── ChatImplement.java
│   └── Servidor.java
└── cliente/src/chat/
    ├── ChatInterfaz.java
    └── Cliente.java
```

## Compilar y ejecutar

### Servidor
```
cd servidor
javac -d bin src\chat\ChatInterfaz.java src\chat\ChatImplement.java src\chat\Servidor.java
java -cp bin chat.Servidor
```

### Cliente (local)
```
cd cliente
javac -d bin src\chat\ChatInterfaz.java src\chat\Cliente.java
java -cp bin chat.Cliente
```

### Cliente (máquina remota)
```
java -cp bin chat.Cliente 192.168.X.X
```
Sustituye la IP por la del servidor.

## Operaciones disponibles
| Opción | Operación |
|--------|-----------|
| 1 | Registrarse |
| 2 | Iniciar sesión |
| 3 | Crear sala |
| 4 | Eliminar sala |
| 5 | Unirse a sala |
| 6 | Abandonar sala |
| 7 | Ver usuarios en sala |
| 8 | Enviar mensaje |
| 9 | Ver mensajes nuevos |
| 0 | Desconectarse |

## Captura Wireshark
(en el pdf entregado)
Filtro recomendado: `rmi` o `tcp.port == 1099`
