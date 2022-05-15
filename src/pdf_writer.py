import os
from pathlib import Path

import docx2pdf
from PyPDF2 import PdfFileMerger

from src.config import Config, Section, Param
from src.word_folder_mgr import WordFolderMgr


class PDFWriter(WordFolderMgr):
    def __init__(self):
        super().__init__()
        self.sz_all_pdf = self.get_pdf_files()

    def get_pdf_files(self) -> list[Path]:
        # Lista donde guardo todos los pdf que genere
        sz_pdf = []

        # Aún no existen los pdf.
        # Recorro los docx que existen, los que voy a convertir a pdf.
        # Genero el nombre que tendrá el pdf resultante de cada uno de ellos
        for file in self.sz_all_docx:
            # Cojo el nombre del docx y le cambio la extensión
            sz_pdf_name = self.word_folder / (file.stem + ".pdf")
            sz_pdf.append(sz_pdf_name)

        return sz_pdf

    def convert_all_word(self):
        # Elimino los archivos temprales
        self.delete_temp_files()

        # Convierto todo a pdf
        docx2pdf.convert(str(self.word_folder))

    def join_pdf(self):

        # Creo un objeto para unir pdf
        merger = PdfFileMerger()
        # Le doy todos los que necesita añadir
        for pdf in self.sz_all_pdf:
            merger.append(str(pdf))

        # Le doy la carpeta y el nombre del pdf
        merger.write(str(Config.get_folder_path(
            Section.DRIVE, Param.PDF_PATH) / "Reseñas.pdf"))
        merger.close()

    def clear_temp_pdf(self):
        # Elimino los archivos pdf temporales que había escrito
        for file in self.sz_all_pdf:
            os.remove(file)
