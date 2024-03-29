import platform
import threading

import __init__
from src.essays.google_api import Drive, join
from src.essays.word import PDFWriter


def create_PDF():

    # Inicialización necesaria para poder abrir Word con multithreading
    if platform.system() == 'Windows':
        import pythoncom
        pythoncom.CoInitialize()

    # Convierto cada word a un pdf
    PDFWriter.convert_all_word()
    # Uno todos los pdf en uno solo
    PDFWriter.join_pdf()
    # Elimino los pdf individuales
    PDFWriter.clear_temp_pdf()


def main():

    # Inicio la conversión a PDF en paralelo
    create_pdf = threading.Thread(target=create_PDF, name="Create PDF")
    create_pdf.start()

    # Mientras creo el PDF, subo los archivos Word
    Drive.update_docx_files()

    # Antes de subir el PDF necesito que esté terminado
    create_pdf.join()
    Drive.update_pdf_files()
    join()


if __name__ == '__main__':
    main()
