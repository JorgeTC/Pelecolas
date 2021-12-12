from pathlib import Path

from src.dlg_config import manage_config

def main(sz_folder):

    manage_config()

    from src.pdf_writer import PDFWriter
    from src.google_drive import Drive

    # Uno todos los word en un único pdf
    # Creo el objeto
    writer = PDFWriter(sz_folder)
    # Convierto cada word a un pdf
    writer.convert_all_word()
    # Uno todos los pdf en uno solo
    writer.join_pdf()
    # Elimino los pdf individuales
    writer.clear_temp_pdf()

    # Actualizo el contenido de google drive
    drive_updater = Drive(sz_folder)
    drive_updater.update_folder()


if __name__ == '__main__':
    sz_peliculas_folder = Path(
        "c:/Users/usuario/Desktop/Jorges things/Reseñas/Películas")

    main(sz_peliculas_folder)
