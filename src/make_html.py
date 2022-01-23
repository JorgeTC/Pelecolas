import os
import re

from src.aux_res_directory import get_res_folder
from src.dlg_make_html import DlgHtml
from src.pelicula import Pelicula
from src.quoter import Quoter
from src.word_reader import WordReader

SZ_INVALID_CHAR = "\/:*?<>|"
SZ_HTML_COMMENT = "\n<!-- {} -->\n".format
SZ_HTML_TITLE = "<!-- \n{}\n -->\n".format
SZ_HTML_FILE = "Reseña {}.html".format

def get_res_html_format(sz_file):
    # Función para leer los formatos del html

    # Abro el archivo html que haya pasado por parámetro
    html_file = open(get_res_folder("Make_html", sz_file))
    # Obtengo la string entera
    sz_file_content = html_file.read()
    # Cierro el archivo que he leído
    html_file.close()
    # Creo un puntero a la función para rellenar la string apropiadamente
    formater = sz_file_content.format

    # Devuelvo la función
    return formater


SZ_HTML_HEADER = get_res_html_format("header.html")
SZ_HTML_PARAGRAPH = get_res_html_format("paragraph.html")
SZ_HTML_QUOTE_PARAGRAPH = get_res_html_format("quote_paragraph.html")
SZ_HTML_HIDDEN_DATA = get_res_html_format("hidden_data.html")


class html(WordReader):

    def __init__(self, folder):
        WordReader.__init__(self, folder)

        # Variable para el nombre del archivo
        self.sz_file_name = ""
        # Creo una lista para guardar el texto de la crítica con el formato html
        self.parrafos_critica = []

        # Objeto Pelicula para guardar los datos que necesito para escribir el html
        # quiero de ella su titulo, año, duración, y director
        self.data = Pelicula()

        # Hago un diccionario con todos los títulos que tienen una crítica escrita
        self.list_titles()

        # Objeto para hacer las citas de forma automática
        self.__citas = Quoter()

    def ask_for_data(self):
        # Diálogo para pedir los datos necesarios para crear el html
        # Necesito darle una lista de todos los títulos que tengo en el word
        dlg = DlgHtml(list(self.titulos.keys()))
        # Llamo al diálogo para que pida por la consola los datos que necesito
        dlg.ask_for_data()
        self.data = dlg.data

    def __get_text(self):
        # Si no tengo los datos de la película, los pido
        if not self.data.titulo:
            self.ask_for_data()

        # Preparo el citador con los datos de la película actual
        self.__citas.titulo = self.data.titulo
        self.__citas.director = self.data.director

        # Empiezo a recorrer los párrafos desde el que sé que inicia la crítica que busco
        for paragraph in self.paragraphs[self.titulos[self.data.titulo]:]:

            if self.is_break_line(paragraph.text):
                # He llegado al final de la crítica. Dejo de leer el documento
                return self.parrafos_critica

            # Convierto el contenido del párrafo a html
            parr_text = self.__parr_to_html(paragraph)

            if not self.parrafos_critica:
                # Si es el primer párrafo, elimino el título
                parr_text = parr_text[len(self.data.titulo):]
                parr_text = parr_text.lstrip(": ")

            # Añado las citas a otras reseñas
            parr_text = self.__citas.quote_parr(parr_text)

            # Añado saltos de línea para un html más legible
            parr_text = parr_text.replace(". ", ".\n")
            # Añado el texto a la lista de párrafos
            self.parrafos_critica.append(parr_text)

        assert("No ha sido posible encontrar la reseña.")

    def __parr_to_html(self, paragraph):
        # Inicializo el párrafo
        parr_text = ""

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
                parr_text += "<i>"
            # Acabo de salir de una cursiva, cierro i
            if not b_curr_it and b_prev_it:
                parr_text += "</i>"

            # Añado el texto
            parr_text += run.text

            # Actualizo la itálica del párrafo anterior
            b_prev_it = b_curr_it

        # Si he terminado el bucle, es posible que me haya dejado la última itálica sin cerrar
        if b_prev_it:
            parr_text += "</i>"

        return parr_text

    def write_html(self):

        self.__get_text()

        # Limpio el titulo de la película por si tiene caracteres no válidos para un archivo de Windows
        self.sz_file_name = "".join(i for i in str(
            self.data.titulo) if i not in SZ_INVALID_CHAR)
        # Compongo el nombre completo del archivo
        self.sz_file_name = SZ_HTML_FILE(self.sz_file_name)
        # Abro el archivo en modo escritura
        reseña = open(self.sz_folder / self.sz_file_name,
                      mode="w", encoding="utf-8")

        # Escribo el título de la película en mayúsculas.
        # Quiero poder copiar del html el nombre del post
        reseña.write(SZ_HTML_TITLE(self.data.titulo.upper()))

        # Escribo el encabezado
        reseña.write(SZ_HTML_COMMENT('Encabezado'))
        reseña.write(SZ_HTML_HEADER("Dir.: " + str(self.data.director)))
        reseña.write(SZ_HTML_HEADER(str(self.data.año)))
        reseña.write(SZ_HTML_HEADER(str(self.data.duracion) + " min."))

        # Iteramos los párrafos
        reseña.write(SZ_HTML_COMMENT('Párrafos'))
        for parrafo in self.parrafos_critica:
            if not self.__is_all_italic(parrafo):
                reseña.write(SZ_HTML_PARAGRAPH(parrafo))
            else:
                reseña.write(SZ_HTML_QUOTE_PARAGRAPH(parrafo))

        # Escribo los botones de Twitter
        reseña.write("\n<br>")
        reseña.write(SZ_HTML_COMMENT('Botón follow'))
        html_follow = open(get_res_folder("Make_html", "follow.html")).read()
        reseña.write(html_follow)
        reseña.write(SZ_HTML_COMMENT('Botón compartir'))
        html_share = open(get_res_folder("Make_html", "share.html")).read()
        reseña.write(html_share)

        # Escribo los datos ocultos
        reseña.write(SZ_HTML_HIDDEN_DATA(year=self.data.año,
                                         director=self.data.director,
                                         country=self.data.pais,
                                         link_fa=self.data.url_FA))

        # Etiquetas para publicar la reseña
        reseña.write(SZ_HTML_COMMENT(self.get_labels()))

        reseña.close()

    def __is_all_italic(self, text: str):
        # Hago listas con todas las listas de itálicas
        apertura_italica = [m.start() for m in re.finditer("<i>", text)]
        cierre_italica = [m.start() for m in re.finditer("</i>", text)]

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

    def get_labels(self):
        # Calcula una string con todas las etiquetas estándar que lleva una reseña
        sz_labels = ""
        # Cronológicas
        # Siglo
        if (int(self.data.año) < 2000):
            siglo = "Siglo XX"
        else:
            siglo = "Siglo XXI"
        sz_labels += siglo + ", "
        # Década
        decade = int(self.data.año) - int(self.data.año) % 10
        decade = str(decade) + "'s"
        sz_labels += decade + ", "
        # Año
        year = str(self.data.año)
        sz_labels += year + ", "

        # Director
        sz_labels += self.data.director + ", "

        # País
        sz_labels += self.data.pais + ", "

        # Devuelvo la lista de etiquetas
        return sz_labels

    def reset(self):
        self.parrafos_critica.clear()
        self.data = Pelicula()
        self.__citas.reset()
        self.sz_file_name = ""

    def delete_file(self):
        # Elimino el último html que he escrito
        os.remove(self.sz_folder / self.sz_file_name)


if __name__ == "__main__":
    Documento = html()
    Documento.write_html()
