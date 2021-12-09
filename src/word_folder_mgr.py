import os

from src.dlg_config import CONFIG


class WordFolderMgr():
    def __init__(self, sz_folder):
        # Carpeta desde la que llamo a la clase
        self.sz_folder = sz_folder
        # Carpeta donde guardo los word
        self.word_folder = self.sz_folder / \
            CONFIG.get_value(CONFIG.S_COUNT_FILMS, CONFIG.P_WORD_FOLDER)
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
