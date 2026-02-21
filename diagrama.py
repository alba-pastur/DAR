from graphviz import Digraph
import sys

# Creamos el diagrama con orientación vertical (Top-to-Bottom)
# Esto es lo más estándar y limpio para diagramas de secuencia.
d = Digraph('G', filename='login_sequence', format='png')
d.attr(rankdir='TB') # El tiempo fluye hacia abajo

# Nodos estéticos como rectángulos (Líneas de vida)
d.attr('node', shape='rectangle', style='filled', fillcolor='lavender', fontname='Arial')
d.node('C', 'CLIENTE\n(App)')
d.node('S', 'SERVIDOR\n(Chat)')

# Mensajes claros y numerados
d.edge('C', 'S', label='1. LOGIN (user, pass)')
d.edge('S', 'C', label='2. RES_OK LOGIN')
d.edge('C', 'S', label='3. ROOM_JOIN (#general)')
d.edge('S', 'C', label='4. EVT_ROOM_UPDATE (Welcome)')

# Intentamos generar un PNG limpio. Si falla, genera un SVG automáticamente.
try:
    d.render(cleanup=True)
    print("¡Diagrama limpio generado con éxito en formato PNG!")
except Exception as e:
    print(f"Aviso de renderizado: {e}")
    # Si falla el PNG, forzamos un SVG, que suele funcionar mejor
    d.format = 'svg'
    d.render(cleanup=True)
    print("Se ha generado el diagrama en formato SVG para garantizar la legibilidad.")