import logging
from src.aux_res_directory import get_res_folder

# Ruta del log único
LOG_FILE = get_res_folder() / "pelecolas.log"


def init_logging():
    # Solo inicializa si no hay handlers configurados
    if logging.getLogger().hasHandlers():
        return

    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s - %(threadName)s - %(filename)s:%(lineno)d - %(levelname)s - %(message)s",
        filename=LOG_FILE,
        datefmt="%d/%m/%Y %H:%M:%S",
        filemode="a",  # append
    )
