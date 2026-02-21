from graphviz import Digraph

# Creamos el diagrama con orientación vertical (Top to Bottom)
d = Digraph('G', filename='login_sequence', format='png')
d.attr(rankdir='TB') 

# Nodos como rectángulos (Líneas de vida)
d.attr('node', shape='rectangle', style='filled', fillcolor='lavender', fontname='Arial')
d.node('C', 'CLIENTE\n(App)')
d.node('S', 'SERVIDOR\n(Chat)')

# Mensajes con flechas
d.edge('C', 'S', label='1. LOGIN (user, pass)')
d.edge('S', 'C', label='2. RES_OK LOGIN')
d.edge('C', 'S', label='3. ROOM_JOIN (#general)')
d.edge('S', 'C', label='4. EVT_ROOM_UPDATE (Welcome)')

d.render(cleanup=True)
print("¡Diagrama limpio generado con éxito!")
