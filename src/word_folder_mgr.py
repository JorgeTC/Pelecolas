import os
from pathlib import Path

from src.config import Config, Section, Param


class WordFolderMgr():
    def __init__(self):
        # Carpeta donde guardo los word
        self.word_folder = Config.get_folder_path(
            Section.COUNT_FILMS, Param.WORD_FOLDER)
        # Lista de todos los archivos word
        self.sz_all_docx = self.get_files()

    def get_files(self):

        # Obtengo todos los archivos de la carpeta
        all_files = [x for x in self.word_folder.iterdir()]
        # Descarto todo lo que no sea un word
        all_files = [x for x in all_files if x.suffix.lower() == ".docx"]
        # Descarto los archivos temporales
        all_files = [x for x in all_files if x.stem[:2] != "~$"]

        return all_files

    def delete_temp_files(self):

        # Obtengo todos los archivos de la carpeta
        temp_files = [x for x in self.word_folder.iterdir()]
        # Descarto todo lo que no sea un word
        temp_files = [x for x in temp_files if x.suffix.lower() == ".docx"]
        # Me quedo con los archivos temporales
        temp_files = [x for x in temp_files if x.stem[:2] == "~$"]

        # Elimino los archivos temporales, no se pueden convertir a pdf
        for temp_file in temp_files:
            os.remove(temp_file)
