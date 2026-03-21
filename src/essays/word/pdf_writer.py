import logging
import platform
from concurrent.futures import ProcessPoolExecutor, as_completed
from functools import partial
from pathlib import Path

from pypdf import PdfWriter

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
    ALL_PDF: list[Path] = get_pdf_files(WordFolderMgr.WORD_FOLDER,
                                        WordFolderMgr.SZ_ALL_DOCX)

    @classmethod
    def convert_all_word(cls):
        logging.debug("Converting all words to pdf files")
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
        pdf_dir = Config.get_folder_path(Section.DRIVE,
                                         Param.PDF_PATH)
        pdf_path = pdf_dir / "Reseñas.pdf"
        logging.debug(f"Joining all PDFs into {pdf_path}")
        # Creo un objeto para unir pdf
        with PdfWriter() as merger:
            # Le doy todos los que necesita añadir
            for pdf in cls.ALL_PDF:
                merger.append(pdf)

            # Le doy la carpeta y el nombre del pdf
            merger.write(pdf_path)

    @classmethod
    def clear_temp_pdf(cls):
        # Elimino los archivos pdf temporales que había escrito
        for file in cls.ALL_PDF:
            file.unlink()

    @classmethod
    def win_convert_all_word(cls):
        logging.debug("Converting all words to pdf files in Windows platform")
        import docx2pdf
        docx2pdf.convert(WordFolderMgr.WORD_FOLDER)

    @classmethod
    def linux_convert_all_word(cls):
        logging.debug("Converting all words to pdf files in Linux platform")
        # Use partial to fix the target_format and dest_folder arguments
        convert_func = partial(cls.libreoffice_convert_file,
                               target_format='pdf',
                               dest_folder=WordFolderMgr.WORD_FOLDER)

        # Convert all DOCX files to PDF in parallel
        with ProcessPoolExecutor() as executor:
            futures = [executor.submit(convert_func, f) for f in WordFolderMgr.SZ_ALL_DOCX]

            logging.debug("Waiting for al the files to be converted to PDF")
            [f.result() for f in as_completed(futures)]
            logging.debug("All Word have been converted to PDF")

    @classmethod
    def libreoffice_convert_file(cls, input_file: Path, target_format: str, dest_folder: Path):
        import subprocess
        logging.debug(f"Writing into {target_format} format {input_file} in dest directory ̣{dest_folder}")
        command_output = subprocess.check_output(['libreoffice',
            '--convert-to', target_format,
            '--outdir', dest_folder,
            input_file])
        logging.debug(f"Finished conversion of {input_file}: {command_output}")
