import os
from pathlib import Path
from datetime import datetime


class BlogCsvMgr():
    # Creo el csv donde guardo los datos de las entradas
    # Obtengo la dirección del csv
    sz_csv_file = Path(__file__).resolve().parent
    sz_csv_file = sz_csv_file / "Make_html"
    sz_csv_file = sz_csv_file / "bog_data.csv"

    # Booleano que me dice si el archivo existe
    exists_csv = os.path.isfile(sz_csv_file)

    # Codificación con la que escribo y leo el csv
    ENCODING = "utf-8"

    def is_needed(self):
        # Si el archivo no existe, hay que crearlo
        if not self.exists_csv:
            return True

        # Si entre la última creación del csv y
        # el momento actual ha pasado un viernes, recalculo el csv
        secs = os.path.getmtime(self.sz_csv_file)
        date_last_modification = datetime.fromtimestamp(secs)
        week_day = date_last_modification.weekday()
        days_till_next_friday = (4 - week_day) % 7
        today = datetime.today()
        passed = today - date_last_modification

        return (passed.days > days_till_next_friday)