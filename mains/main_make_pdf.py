from pathlib import Path

from src.dlg_config import manage_config

def main(sz_folder):

    manage_config()

    from src.pdf_writer import PDFWriter

    writer = PDFWriter(sz_folder)
    writer.convert_all_word()
    writer.join_pdf()
    writer.clear_temp_pdf()


if __name__ == '__main__':
    sz_peliculas_folder = Path(
        "c:/Users/usuario/Desktop/Jorges things/Reseñas/Películas")

    main(sz_peliculas_folder)
