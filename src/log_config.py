import logging
from src.aux_res_directory import get_res_folder

# Ruta del log único
LOG_FILE = get_res_folder() / "pelecolas.log"

_old_factory = logging.getLogRecordFactory()

def _record_factory(*args, **kwargs):
    record = _old_factory(*args, **kwargs)
    # Creamos un argumento nuevo en el log: 'loc'
    # Se compone del nombre del archivo, ':' y el número de linea
    # Creamos el atributo en vez de componerlo en la llamada
    # para poder formatear el número de caracteres
    record.loc = f"{record.filename}:{record.lineno}"
    return record

logging.setLogRecordFactory(_record_factory)


def init_logging():
    # Solo inicializa si no hay handlers configurados
    if logging.getLogger().hasHandlers():
        return

    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s %(levelname).1s %(threadName)-20.20s %(loc)-26s | %(message)s",
        filename=LOG_FILE,
        datefmt="%d/%m/%Y %H:%M:%S",
        filemode="a",  # append
    )
