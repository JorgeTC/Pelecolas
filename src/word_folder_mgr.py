import os
from pathlib import Path

from src.config import Config, Param, Section


def get_files(word_folder: Path) -> list[Path]:

    # Obtengo todos los archivos de la carpeta
    all_files = [x for x in word_folder.iterdir()]
    # Descarto todo lo que no sea un word
    all_files = [x for x in all_files if x.suffix.lower() == ".docx"]
    # Descarto los archivos temporales
    all_files = [x for x in all_files if x.stem[:2] != "~$"]

    return all_files


class WordFolderMgr():
    # Carpeta donde guardo los word
    WORD_FOLDER = Config.get_folder_path(
        Section.COUNT_FILMS, Param.WORD_FOLDER)
    # Lista de todos los documentos
    SZ_ALL_DOCX: list[Path] = get_files(WORD_FOLDER)

    @classmethod
    def delete_temp_files(cls):

        # Obtengo todos los archivos de la carpeta
        temp_files = (x for x in cls.WORD_FOLDER.iterdir())
        # Descarto todo lo que no sea un word
        temp_files = (x for x in temp_files if x.suffix.lower() == ".docx")
        # Me quedo con los archivos temporales
        temp_files = (x for x in temp_files if x.stem[:2] == "~$")

        # Elimino los archivos temporales, no se pueden convertir a pdf
        for temp_file in temp_files:
            os.remove(temp_file)
