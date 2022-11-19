import sys
from pathlib import Path


def add_src_folder_in_path():
    # Obtengo la ruta de la carpeta de mains
    SCRIPT_DIR = Path(__file__).parent
    # Subo a la carpeta del proyecto
    CODE_DIR = SCRIPT_DIR.parent
    # La añado a las rutas del sistema
    sys.path.append(str(CODE_DIR))


# Añado la carpeta del proyecto a las rutas de Python
add_src_folder_in_path()
