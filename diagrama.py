from graphviz import Digraph

# Crear el diagrama de secuencia
d = Digraph('G', filename='login_sequence', format='png')
d.attr(rankdir='LR', splines='line')

# Configuración estética
d.attr('node', shape='rectangle', style='filled', fillcolor='lightblue2', fontname='Arial')

# Definir las "Líneas de Vida" (los actores)
with d.subgraph() as s:
    s.attr(rank='same')
    s.node('C', 'CLIENTE\n(Usuario)')
    s.node('S', 'SERVIDOR\n(Chat)')

# Mensajes de la secuencia (de arriba a abajo)
# Usamos etiquetas claras y flechas rectas
d.edge('C', 'S', label=' 1. LOGIN (user, pass)')
d.edge('S', 'C', label=' 2. RES_OK LOGIN')
d.edge('C', 'S', label=' 3. ROOM_JOIN (#sala1)')
d.edge('S', 'C', label=' 4. EVT_ROOM_UPDATE (Welcome)')

# Guardar y generar
d.render(cleanup=True)
print("¡Diagrama profesional generado como login_sequence.png!")