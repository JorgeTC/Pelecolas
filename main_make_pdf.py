from dlg_config import CONFIG
from docx2pdf import convert
from pathlib import Path
from PyPDF2 import PdfFileMerger
import os



def get_files(sz_folder):
    # Carpeta donde están guardados los archivos word
    word_folder = CONFIG.get_value(CONFIG.S_COUNT_FILMS, CONFIG.P_WORD_FOLDER)
    # Si en el archivo de configuración se especifica una carpeta, busco en ella
    if word_folder:
        folder = sz_folder / word_folder

    # Me espero un único archivo docx
    all_files = [x for x in folder.iterdir()]
    all_files = [x for x in all_files if x.suffix.lower() == ".docx"]

    return all_files

def convert_all_word(files):

    # Lista donde guardo todos los pdf que genere
    sz_pdf = []

    for file in files:
        sz_pdf_name = file.parent / ( file.stem + ".pdf" )
        sz_pdf.append(sz_pdf_name)

    sz_folder = str(files[0].parent) + "\\"
    #convert(sz_folder)

    return sz_pdf

def join_pdf(sz_folder, pdfs):

    merger = PdfFileMerger()
    for pdf in pdfs:
        merger.append(str(pdf))

    merger.write(str(sz_folder / "Reseñas.pdf") )
    merger.close()

def clear_pdf(pdfs):
    for file in pdfs:
        os.remove(file)


def main(sz_folder):
    # Obtengo el nombre de todos los word que existen
    files = get_files(sz_folder)

    files_pdf = convert_all_word(files)

    join_pdf(sz_folder, files_pdf)

    clear_pdf(files_pdf)

if __name__ == '__main__':
    sz_peliculas_folder = Path("c:/Users/usuario/Desktop/Jorges things/Reseñas/Películas")

    main( sz_peliculas_folder )
