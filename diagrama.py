from graphviz import Digraph

# Creamos el diagrama de secuencia
dot = Digraph('Chat_Sequence', comment='Operacion de Login')
dot.attr(rankdir='TB')

# Definimos los nodos (Cliente y Servidor)
dot.node('C', 'Cliente')
dot.node('S', 'Servidor')

# Definimos el intercambio de mensajes según vuestro protocolo
dot.edge('C', 'S', label='LOGIN user pass')
dot.edge('S', 'C', label='RES_OK LOGIN')

# Generamos la imagen
dot.render('login_sequence', format='png', cleanup=True)
print("Diagrama generado con éxito como login_sequence.png")