import threading

from src.dlg_config import manage_config


def create_PDF():

    from src.pdf_writer import PDFWriter
    import pythoncom

    # Iniclaización necesaria para poder abrir Word con multithreading
    pythoncom.CoInitialize()

    writer = PDFWriter()
    # Convierto cada word a un pdf
    writer.convert_all_word()
    # Uno todos los pdf en uno solo
    writer.join_pdf()
    # Elimino los pdf individuales
    writer.clear_temp_pdf()


def main():

    manage_config()

    from src.google_drive import Drive

    # Inicio la conversión a PDF en paralelo
    create_pdf = threading.Thread(name="Create_PDF", target=create_PDF)
    create_pdf.start()

    # Actualizo el contenido de google drive
    drive_updater = Drive()
    # Antes de subir los archivos necesito que el PDF esté terminado
    create_pdf.join()
    drive_updater.update_folder()


if __name__ == '__main__':
    main()
