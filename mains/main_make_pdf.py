from pathlib import Path
import threading

from src.dlg_config import manage_config

def create_PDF(sz_folder):

    from src.pdf_writer import PDFWriter
    import pythoncom

    # Iniclaización necesaria para poder abrir Word con multithreading
    pythoncom.CoInitialize()

    writer = PDFWriter(sz_folder)
    # Convierto cada word a un pdf
    writer.convert_all_word()
    # Uno todos los pdf en uno solo
    writer.join_pdf()
    # Elimino los pdf individuales
    writer.clear_temp_pdf()


def main(sz_folder):

    manage_config()

    from src.google_drive import Drive

    # Inicio la conversión a PDF en paralelo
    create_pdf = threading.Thread(name="Create_PDF", target=create_PDF, args=[sz_folder])
    create_pdf.start()

    # Actualizo el contenido de google drive
    drive_updater = Drive(sz_folder)
    # Antes de subir los archivos necesito que el PDF esté terminado
    create_pdf.join()
    drive_updater.update_folder()


if __name__ == '__main__':
    sz_peliculas_folder = Path(
        "c:/Users/usuario/Desktop/Jorges things/Reseñas/Películas")

    main(sz_peliculas_folder)
