import threading

from src.config import manage_config


def create_PDF():

    from src.pdf_writer import PDFWriter
    import pythoncom

    # Inicialización necesaria para poder abrir Word con multithreading
    pythoncom.CoInitialize()

    # Convierto cada word a un pdf
    PDFWriter.convert_all_word()
    # Uno todos los pdf en uno solo
    PDFWriter.join_pdf()
    # Elimino los pdf individuales
    PDFWriter.clear_temp_pdf()


def main():

    manage_config()

    from src.google_api.google_drive import Drive

    # Inicio la conversión a PDF en paralelo
    create_pdf = threading.Thread(target=create_PDF)
    create_pdf.start()

    # Mientras creo el PDF, subo los archivos Word
    Drive.update_docx_files()

    # Antes de subir el PDF necesito que esté terminado
    create_pdf.join()
    Drive.update_pdf_files()


if __name__ == '__main__':
    main()
