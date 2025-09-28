import sys
from pathlib import Path
import logging


def add_src_folder_in_path():
    # Obtengo la ruta de la carpeta de mains
    SCRIPT_DIR = Path(__file__).parent
    # Subo a la carpeta del proyecto
    CODE_DIR = SCRIPT_DIR.parent
    # La añado a las rutas del sistema
    sys.path.append(str(CODE_DIR))


# Añado la carpeta del proyecto a las rutas de Python
add_src_folder_in_path()

# Inicializo el logging
from src.log_config import init_logging
init_logging()

main_module = __import__("__main__")
main_file = main_module.__file__
main_name = Path(main_file).name
logging.debug(f"***** {main_name} *****")
