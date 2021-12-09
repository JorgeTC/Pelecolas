import os
import csv
from pathlib import Path
from datetime import datetime

from src.dlg_config import CONFIG
from src.poster import POSTER

class CSV_COLUMN:
    TITLE = 0
    LINK = 1
    DIRECTOR = 2
    YEAR = 3

class BlogCsvMgr():
    # Creo el csv donde guardo los datos de las entradas
    # Obtengo la dirección del csv
    sz_csv_file = Path("res")
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

        # Si la configuración fuerza la creación del CSV, hay que crearlo
        if CONFIG.get_bool(CONFIG.S_HTML, CONFIG.P_SCRAP_BLOG):
            # Devuelvo a False, la próxima vez se seguirá el algoritmo habitual
            CONFIG.set_value(CONFIG.S_HTML, CONFIG.P_SCRAP_BLOG, False)
            return True

        # Compruebo que el archivo no esté vacío
        csv_file_temp = open(self.sz_csv_file, encoding=self.ENCODING)
        csv_reader = csv.reader(csv_file_temp, delimiter=",")
        if len(list(csv_reader)) < 2:
            return True

        # Si entre la última creación del csv y
        # el momento actual ha pasado un viernes, recalculo el csv
        secs = os.path.getmtime(self.sz_csv_file)
        date_last_modification = datetime.fromtimestamp(secs)

        # Compruebo si se ha publicado algo en el blog
        # desde la última vez que se hizo el csv
        new_posts = POSTER.get_published_from_date(date_last_modification)

        return len(new_posts) > 0

    def open_to_read(self):
        self.csv_file = open(self.sz_csv_file, encoding=self.ENCODING)
        csv_reader = csv.reader(self.csv_file, delimiter=",")
        # Convierto lo leído en listas
        # Es una lista que contiene cada linea expresada como lista
        csv_reader = list(csv_reader)

        try:
            # Devuelvo la lista sin la primera fila, que tiene los encabezados
            return csv_reader[1:]
        except:
            return []

    def open_to_write(self):
        self.csv_file = open(self.sz_csv_file, 'w',
                               encoding=self.ENCODING, newline='')
        csv_writer = csv.writer(self.csv_file)

        return csv_writer
