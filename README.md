# DAR
PRÁCTICA DAR

Inicializar un proyecto nuevo desde cero
Entra en la carpeta: cd "ruta\de\tu\carpeta"

Inicializa: git init

Conecta con GitHub: git remote add origin https://github.com/TU_USUARIO/NOMBRE_REPO.git

Crea la rama principal: git branch -M main

Añadir, confirmar y subir archivos iniciales
Bash
git add .
git commit -m "Primer commit"
git push -u origin main
Si vas a empezar a trabajar después de un tiempo (para actualizar tu PC)
Bash
git pull origin main --rebase
Cuando termines de programar o modificar archivos
1. Añadir todo lo nuevo:

Bash
git add .
2. Guardar el "paquete":

Bash
git commit -m "Descripción de lo que has hecho"
3. Subir a la nube:

Bash
git push origin main
