import os

import docx2pdf
from PyPDF2 import PdfFileMerger

from dlg_config import CONFIG
from word_folder_mgr import WordFolderMgr


class PDFWriter(WordFolderMgr):
    def __init__(self, sz_folder):
        super().__init__(sz_folder)
        self.sz_all_pdf = self.get_pdf_files()

    def get_pdf_files(self):
        # Lista donde guardo todos los pdf que genere
        sz_pdf = []

        for file in self.sz_all_docx:
            sz_pdf_name = self.word_folder / (file.stem + ".pdf")
            sz_pdf.append(sz_pdf_name)

        return sz_pdf

    def convert_all_word(self):
        # Elimino los archivos temprales
        self.delete_temp_files()

        # Convierto todo a pdf
        docx2pdf.convert(str(self.word_folder))

    def join_pdf(self):

        merger = PdfFileMerger()
        for pdf in self.sz_all_pdf:
            merger.append(str(pdf))

        merger.write(str(self.sz_folder / "Reseñas.pdf"))
        merger.close()

    def clear_pdf(self):
        for file in self.sz_all_pdf:
            os.remove(file)
