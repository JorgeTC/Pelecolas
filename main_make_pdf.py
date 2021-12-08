import os
from pathlib import Path

import docx2pdf
from PyPDF2 import PdfFileMerger

from dlg_config import CONFIG


class PDFWriter():
    def __init__(self, sz_folder):
        self.sz_folder = sz_folder
        self.word_folder = self.sz_folder / CONFIG.get_value(CONFIG.S_COUNT_FILMS, CONFIG.P_WORD_FOLDER)
        self.sz_all_docx = self.get_files()
        self.sz_all_pdf = self.get_pdf_files()

    def get_files(self):

        # Obtengo todos los archivos de la carpeta
        all_files = [x for x in self.word_folder.iterdir()]
        # Descarto todo lo que no sea un word
        all_files = [x for x in all_files if x.suffix.lower() == ".docx"]
        # Descarto los archivos temporales
        all_files = [x for x in all_files if x.stem[:2] != "~$"]

        return all_files

    def get_pdf_files(self):
        # Lista donde guardo todos los pdf que genere
        sz_pdf = []

        for file in self.sz_all_docx:
            sz_pdf_name = self.word_folder / ( file.stem + ".pdf" )
            sz_pdf.append(sz_pdf_name)

        return sz_pdf

    def convert_all_word(self):
        # Elimino los archivos temprales
        # Obtengo todos los archivos de la carpeta
        temp_files = [x for x in self.word_folder.iterdir()]
        # Descarto todo lo que no sea un word
        temp_files = [x for x in temp_files if x.suffix.lower() == ".docx"]
        # Descarto los archivos temporales
        temp_files = [x for x in temp_files if x.stem[:2] == "~$"]

        # Elimino los archivos temporales, no se pueden convertir a pdf
        for temp_file in temp_files:
            os.remove(temp_file)

        # Convierto todo a pdf
        docx2pdf.convert(str(self.word_folder))

    def join_pdf(self):

        merger = PdfFileMerger()
        for pdf in self.sz_all_pdf:
            merger.append(str(pdf))

        merger.write(str(self.sz_folder / "Reseñas.pdf") )
        merger.close()

    def clear_pdf(self):
        for file in self.sz_all_pdf:
            os.remove(file)


def main(sz_folder):

    writer = PDFWriter(sz_folder)
    writer.convert_all_word()
    writer.join_pdf()
    writer.clear_pdf()

if __name__ == '__main__':
    sz_peliculas_folder = Path("c:/Users/usuario/Desktop/Jorges things/Reseñas/Películas")

    main( sz_peliculas_folder )
