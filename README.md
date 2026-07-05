# Sistema de reconocimiento facial

Registra una asistencia por persona y día mediante la cámara, y guarda los datos en un CSV que puede abrirse en el visor Angular incluido.

## Preparar y ejecutar Python

```bash
python3 -m venv venv
source venv/bin/activate
python -m pip install -r requirements.txt
python program.py
```

En macOS, concede acceso a la cámara a Terminal o a VS Code cuando el sistema lo solicite. Pulsa `q` en la ventana de vídeo para cerrar el programa.

El CSV se crea en la raíz del proyecto con el nombre de la fecha, por ejemplo `2026-07-05.csv`.

## Abrir el visor web

En otra terminal:

```bash
cd frontend
npm install
npm start
```

Abre `http://localhost:4200/` y selecciona el CSV. El archivo se procesa solo en el navegador.
