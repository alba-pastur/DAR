# DAR
PRÁCTICA DAR

Inicializar un proyecto nuevo desde cero

# 1. Entra en la carpeta: 
cd "ruta\de\tu\carpeta"
# 2. Inicializa: git init
Conecta con GitHub: git remote add origin https://github.com/TU_USUARIO/NOMBRE_REPO.git
Crea la rama principal: git branch -M main

# 3. Añade, confirma y sube:
Bash
git add .
git commit -m "Primer commit"
git push -u origin main

# Si vas a empezar a trabajar después de un tiempo (para actualizar tu PC):
Bash
git pull origin main --rebase

# Cuando termines de programar o modificar archivos:
Añadir todo lo nuevo:

Bash
git add .
Guardar el "paquete" con un mensaje:

Bash
git commit -m "Aquí pones lo que has hecho, ej: añadido función de login"
Enviar a la nube:

Bash
git push origin main
