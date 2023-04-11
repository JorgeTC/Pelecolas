import os
import re
from contextlib import suppress
from io import StringIO
from typing import TextIO

from docx.text.paragraph import Paragraph

from src.aux_res_directory import get_res_folder
from src.config import Config, Param, Section
from src.pelicula import Pelicula

from ..word import WordReader
from .dlg_make_html import DlgHtml
from .quoter import Quoter

SZ_INVALID_CHAR = "\\/:*?<>|"
SZ_HTML_COMMENT = "\n<!-- {} -->\n".format
SZ_HTML_TITLE = "<!-- \n{}\n -->\n".format
SZ_HTML_BREAK_LINE = "\n<br>"
SZ_HTML_FILE = "Reseña {}.html".format


def get_res_html_format(sz_file):
    # Función para leer los formatos del html

    # Abro el archivo html que haya pasado por parámetro
    with open(get_res_folder("Make_html", sz_file)) as html_file:
        # Obtengo la string entera
        sz_file_content = html_file.read()
    # Devuelvo la función para rellenar la string apropiadamente
    return sz_file_content.format


SZ_HTML_HEADER = get_res_html_format("header.html")
SZ_HTML_PARAGRAPH = get_res_html_format("paragraph.html")
SZ_HTML_QUOTE_PARAGRAPH = get_res_html_format("quote_paragraph.html")
SZ_HTML_HIDDEN_DATA = get_res_html_format("hidden_data.html")


class Html:

    HTML_OUTPUT_FOLDER = Config.get_folder_path(
        Section.HTML, Param.OUTPUT_PATH_HTML)

    def __init__(self, film: Pelicula = None):

        # Variable para el nombre del archivo
        self.sz_file_name = ""
        # Creo una lista para guardar el texto de la crítica con el formato html
        self.parrafos_critica: list[str] = []

        # Objeto Pelicula para guardar los datos que necesito para escribir el html
        # quiero de ella su titulo, año, duración, y director
        self.data = Pelicula() if film is None else film

    def ask_for_data(self):
        # Diálogo para pedir los datos necesarios para crear el html
        # Necesito darle una lista de todos los títulos que tengo en el word
        dlg = DlgHtml(WordReader.list_titles())
        # Llamo al diálogo para que pida por la consola los datos que necesito
        dlg.ask_for_data()
        self.data = dlg.data

    def __get_text(self):
        # Si no tengo los datos de la película, los pido
        if not self.data.titulo:
            self.ask_for_data()

        # Preparo el citador con los datos de la película actual
        citas = Quoter(self.data.titulo, self.data.director)

        # Empiezo a recorrer los párrafos desde el que sé que inicia la crítica que busco
        for paragraph in WordReader.iter_review(self.data.titulo):
            # Convierto el contenido del párrafo a html
            parr_text = parr_to_html(paragraph)

            if not self.parrafos_critica:
                # Si es el primer párrafo, elimino el título
                parr_text = parr_text[len(self.data.titulo):]
                parr_text = parr_text.lstrip(": ")

            # Añado las citas a otras reseñas
            parr_text = citas.quote_parr(parr_text)

            # Añado saltos de línea para un html más legible
            parr_text = re.sub(r"([.!?…>:]) ", r"\1\n", parr_text)
            # Añado el texto a la lista de párrafos
            self.parrafos_critica.append(parr_text)

        if not self.parrafos_critica:
            assert ("No ha sido posible encontrar la reseña.")
        return self.parrafos_critica

    def write_html(self):

        self.__get_text()

        # Limpio el titulo de la película por si tiene caracteres no válidos para un archivo de Windows
        self.sz_file_name = "".join(i for i in str(self.data.titulo)
                                    if i not in SZ_INVALID_CHAR)
        # Compongo el nombre completo del archivo
        self.sz_file_name = SZ_HTML_FILE(self.sz_file_name)
        # Abro el archivo en modo escritura
        with open(self.HTML_OUTPUT_FOLDER / self.sz_file_name,
                  mode="w", encoding="utf-8") as html_file:
            self.fill_html_file(html_file)

    def fill_html_file(self, html_file: TextIO):
        # Escribo el título de la película en mayúsculas.
        html_file.write(SZ_HTML_TITLE(self.data.titulo.upper()))

        # Escribo el estilo css si así me lo indica el ini
        if Config.get_bool(Section.HTML, Param.ADD_STYLE):
            html_file.write("<style>\n")
            with open(get_res_folder("Make_html", "template.css")) as css_code:
                html_file.write(css_code.read())
            html_file.write("</style>\n")

        # Escribo el encabezado
        html_file.write(SZ_HTML_COMMENT('Encabezado'))
        html_file.write(SZ_HTML_HEADER(director=self.data.director,
                                       year=self.data.año,
                                       duration=self.data.duracion,
                                       image_url=self.data.url_image))

        # Iteramos los párrafos
        html_file.write(SZ_HTML_COMMENT('Párrafos'))
        html_file.write('<section class="review-body">\n')
        for parrafo in self.parrafos_critica:
            if is_quote_parr(parrafo):
                html_file.write(SZ_HTML_QUOTE_PARAGRAPH(parrafo))
            else:
                html_file.write(SZ_HTML_PARAGRAPH(parrafo))
        html_file.write('</section>\n')

        # Escribo los botones de Twitter
        html_file.write(SZ_HTML_BREAK_LINE)
        html_file.write("\n<footer>")
        html_file.write(SZ_HTML_COMMENT('Botón follow'))
        with open(get_res_folder("Make_html", "follow.html")) as follow_code:
            html_follow = follow_code.read()
        html_file.write(html_follow)
        html_file.write(SZ_HTML_COMMENT('Botón compartir'))
        with open(get_res_folder("Make_html", "share.html")) as share_code:
            html_share = share_code.read()
        html_file.write(html_share)

        # Escribo los datos ocultos
        html_file.write(SZ_HTML_HIDDEN_DATA(year=self.data.año,
                                            director=self.data.director,
                                            country=self.data.pais,
                                            link_fa=self.data.url_FA,
                                            film_title=self.data.titulo,
                                            labels=get_labels(self.data),
                                            duration=self.data.duracion,
                                            link_image=self.data.url_image))
        html_file.write("\n</footer>")

    def delete_file(self):
        # Elimino el último html que he escrito
        os.remove(self.HTML_OUTPUT_FOLDER / self.sz_file_name)


def get_labels(film: Pelicula) -> str:
    # Calcula una lista con todas las etiquetas estándar que lleva una reseña
    labels: list[str] = []
    # Cronológicas
    with suppress(TypeError):
        # Siglo
        labels.append("Siglo XX" if int(film.año) < 2000 else "Siglo XXI")
        # Década
        decade = int(film.año) - int(film.año) % 10
        labels.append(f"{decade}'s")
        # Año
        labels.append(str(film.año))

    # Director
    if film.director:
        labels.append(film.director)

    # País
    if film.pais:
        labels.append(film.pais)

    # Devuelvo la lista de etiquetas
    return ", ".join(label for label in labels if label)


def is_quote_parr(text: str) -> bool:
    return is_all_italic(text) or is_dialogue(text)


def is_dialogue(text: str) -> bool:
    # Será diálogo si empieza con guión largo
    return bool(re.match(r"^(<i>)?—", text))


def is_all_italic(text: str) -> bool:
    # Hago listas con todas las listas de itálicas
    apertura_italica = [m.start() for m in re.finditer(r"<i>", text)]
    cierre_italica = [m.start() for m in re.finditer(r"</i>", text)]

    # Me espero que ambas listas tengan la misma longitud
    # Si hay más de una itálica, hay algún trozo de párrafo que no está en cursiva
    if len(apertura_italica) != 1 or len(cierre_italica) != 1:
        return False

    # Compruebo que la itálica empiece con el párrafo
    if apertura_italica[0] != 0:
        return False
    # Compruebo que la itálica termine con el párrafo
    if cierre_italica[0] != len(text) - len("</i>"):
        return False

    return True


def parr_to_html(paragraph: Paragraph) -> str:
    # Inicializo el párrafo
    parr_text = StringIO()

    # Conservo las cursivas
    # Si hay dos cursivas consecutivas las quiero unir como una sola
    b_prev_it = False
    b_curr_it = False

    for run in paragraph.runs:
        # Si todo son espacios, realmente no ha habido cambio de cursivas
        if not run.text.isspace():
            b_curr_it = run.italic

        # Acabo de entrar a una cursiva, abro i
        if b_curr_it and not b_prev_it:
            parr_text.write("<i>")
        # Acabo de salir de una cursiva, cierro i
        if not b_curr_it and b_prev_it:
            parr_text.write("</i>")

        # Añado el texto
        parr_text.write(run.text)

        # Actualizo la itálica del párrafo anterior
        b_prev_it = b_curr_it

    # Si he terminado el bucle, es posible que me haya dejado la última itálica sin cerrar
    if b_prev_it:
        parr_text.write("</i>")

    return parr_text.getvalue()
