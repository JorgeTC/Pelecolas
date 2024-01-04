import os
import platform
from pathlib import Path

from pypdf import PdfMerger

from src.config import Config, Param, Section

from .word_folder_mgr import WordFolderMgr


def get_pdf_files(docx_folder: Path, docx_list: list[Path]) -> list[Path]:
    # Lista donde guardo todos los pdf que genere
    # Aún no existen los pdf.
    # Recorro los docx que existen, los que voy a convertir a pdf.
    # Genero el nombre que tendrá el pdf resultante de cada uno de ellos
    return [docx_folder / f"{file.stem}.pdf"
            for file in docx_list]


class PDFWriter:
    SZ_ALL_PDF: list[Path] = get_pdf_files(
        WordFolderMgr.WORD_FOLDER, WordFolderMgr.SZ_ALL_DOCX)

    @classmethod
    def convert_all_word(cls):
        # Elimino los archivos temprales
        WordFolderMgr.delete_temp_files()

        # Convierto todo a pdf
        if platform.system() == 'Windows':
            cls.win_convert_all_word()
        elif platform.system() == 'Linux':
            cls.linux_convert_all_word()
        else:
            raise NotImplementedError

    @classmethod
    def join_pdf(cls):

        # Creo un objeto para unir pdf
        merger = PdfMerger()
        # Le doy todos los que necesita añadir
        for pdf in cls.SZ_ALL_PDF:
            merger.append(pdf)

        # Le doy la carpeta y el nombre del pdf
        merger.write(Config.get_folder_path(
            Section.DRIVE, Param.PDF_PATH) / "Reseñas.pdf")
        merger.close()

    @classmethod
    def clear_temp_pdf(cls):
        # Elimino los archivos pdf temporales que había escrito
        for file in cls.SZ_ALL_PDF:
            os.remove(file)

    @classmethod
    def win_convert_all_word(cls):
        import docx2pdf
        docx2pdf.convert(WordFolderMgr.WORD_FOLDER)

    @classmethod
    def linux_convert_all_word(cls):
        for docx in WordFolderMgr.SZ_ALL_DOCX:
            cls.libreoffice_convert_file(docx,
                                         'pdf', WordFolderMgr.WORD_FOLDER)

    @classmethod
    def libreoffice_convert_file(cls, input_file: Path, target_format: str, dest_folder: Path):
        import subprocess
        subprocess.check_output(['libreoffice',
                                 '--convert-to', target_format,
                                 '--outdir', dest_folder,
                                 input_file])
