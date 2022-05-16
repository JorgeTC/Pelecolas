import csv
import enum
import os
from datetime import datetime
from typing import Iterable

from src.aux_res_directory import get_res_folder
from src.config import Config, Param, Section
from src.poster import Poster


class CSV_COLUMN(int, enum.Enum):
    TITLE = 0
    LINK = enum.auto()
    DIRECTOR = enum.auto()
    YEAR = enum.auto()


class BlogCsvMgr():
    # Creo el csv donde guardo los datos de las entradas
    # Obtengo la dirección del csv
    SZ_CSV_FILE = get_res_folder("Make_html", "bog_data.csv")

    # Codificación con la que escribo y leo el csv
    ENCODING = "utf-8"

    @classmethod
    def exists_csv(cls) -> bool:
        return os.path.isfile(cls.SZ_CSV_FILE)

    @classmethod
    def is_needed(cls) -> bool:
        # Si el archivo no existe, hay que crearlo
        if not cls.exists_csv():
            return True

        # Si la configuración fuerza la creación del CSV, hay que crearlo
        if Config.get_bool(Section.HTML, Param.SCRAP_BLOG):
            # Devuelvo a False, la próxima vez se seguirá el algoritmo habitual
            Config.set_value(Section.HTML, Param.SCRAP_BLOG, False)
            return True

        # Compruebo que el archivo no esté vacío
        csv_file_temp = open(cls.SZ_CSV_FILE, encoding=cls.ENCODING)
        csv_reader = csv.reader(csv_file_temp, delimiter=",")
        if len(list(csv_reader)) < 2:
            return True

        # Si entre la última creación del csv y
        # el momento actual ha pasado un viernes, recalculo el csv
        secs = os.path.getmtime(cls.SZ_CSV_FILE)
        date_last_modification = datetime.fromtimestamp(secs)

        # Compruebo si se ha publicado algo en el blog
        # desde la última vez que se hizo el csv
        new_posts = Poster.get_published_from_date(date_last_modification)

        return len(new_posts) > 0

    @classmethod
    def open_to_read(cls) -> list[list[str]]:
        with open(cls.SZ_CSV_FILE, encoding=cls.ENCODING) as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=",")
            # Convierto lo leído en listas
            # Es una lista que contiene cada linea expresada como lista
            csv_reader = list(csv_reader)

        try:
            # Devuelvo la lista sin la primera fila, que tiene los encabezados
            return csv_reader[1:]
        except:
            return []

    @classmethod
    def write(cls, header: Iterable[str], rows: Iterable[Iterable[str]]) -> None:
        with open(cls.SZ_CSV_FILE, 'w', encoding=cls.ENCODING, newline='') as csv_file:
            csv_writer = csv.writer(csv_file)
            csv_writer.writerow(header)
            csv_writer.writerows(rows)
