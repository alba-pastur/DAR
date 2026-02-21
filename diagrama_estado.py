from graphviz import Digraph

# Creamos el diagrama de estados del servidor
dot = Digraph('Servidor_Estados', comment='Ciclo de vida del Servidor')
dot.attr(rankdir='LR')

# Definimos los nodos (Estados)
dot.node('DISC', 'DESCONECTADO')
dot.node('AUTH', 'AUTENTICANDO')
dot.node('LOBBY', 'LOBBY')
dot.node('ROOM', 'IN_ROOM')

# Definimos las transiciones
dot.edge('DISC', 'AUTH', label='Conexión TCP')
dot.edge('AUTH', 'LOBBY', label='LOGIN OK')
dot.edge('LOBBY', 'ROOM', label='ROOM_JOIN')
dot.edge('ROOM', 'LOBBY', label='ROOM_LEAVE')
dot.edge('LOBBY', 'DISC', label='QUIT')
dot.edge('ROOM', 'DISC', label='QUIT')

# Generamos la imagen
dot.render('servidor_estados', format='png', cleanup=True)
print("Diagrama de estados generado con éxito como servidor_estados.png")