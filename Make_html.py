import re

import docx

from .dlg_make_html import DlgHtml
from .Pelicula import Pelicula
from .WordReader import WordReader

SZ_INVALID_CHAR = "\/:*?<>|"


class html():

    def __init__(self, folder):
        self.folder = folder
        # Abro el documento para leerlo
        self.doc = docx.Document(folder / "Películas.docx")

        self.parrafos_critica = []
        # Objeto Pelicula para guardar los datos que necesito para escribir el html
        # quiero de ella su titulo, año, duración, y director
        self.data = Pelicula()

        # Hago un diccionario con todos los títulos que tienen una crítica escrita
        reader = WordReader(folder)
        reader.list_titles()
        self.titulos = reader.titulos

    def ask_for_data(self):
        # Diálogo para pedir los datos necesarios para crear el html
        # Necesito darle una lista de todos los títulos que tengo en el word
        dlg = DlgHtml(list(self.titulos.keys()))
        # Llamo al diálogo para que pida por la consola los datos que necesito
        dlg.ask_for_data()
        self.data = dlg.data

    @staticmethod
    def __fin_de_parrafo(text):
        return text == "" or text == "\t"

    def __get_text(self):
        # Si no tengo los datos de la película, los pido
        if not self.data.titulo:
            self.ask_for_data()
        # Empiezo a recorrer los párrafos desde el que sé que inicia la crítica que busco
        for paragraph in self.doc.paragraphs[self.titulos[self.data.titulo]:]:

            if self.__fin_de_parrafo(paragraph.text):
                # He llegado al final de la crítica. Dejo de leer el documento
                return self.parrafos_critica

            # Convierto el contenido del párrafo a html
            parr_text = self.__parr_to_html(paragraph)

            if not self.parrafos_critica:
                # Si es el primer párrafo, elimino el título
                parr_text = parr_text[len(self.data.titulo):]
                parr_text = parr_text.lstrip(": ")

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
        sz_file_name = "".join(i for i in str(
            self.data.titulo) if i not in SZ_INVALID_CHAR)
        # Compongo el nombre completo del archivo
        sz_file_name = "Reseña " + sz_file_name + ".html"
        # Abro el archivo en modo escritura
        reseña = open(self.folder / sz_file_name, mode="w", encoding="utf-8")

        # Escribo el encabezado
        reseña.write("<!-- Encabezado -->\n")
        self.__write_header_data(reseña, "Dir.: " + str(self.data.director))
        self.__write_header_data(reseña, str(self.data.año))
        self.__write_header_data(reseña, str(self.data.duracion) + " min.")

        # Iteramos los párrafos
        reseña.write("\n<!-- Párrafos -->\n")
        for parrafo in self.parrafos_critica:
            self.__write_paragraph(reseña, parrafo)

        # Escribo los botones de Twitter
        reseña.write("\n<p>")
        reseña.write("\n<!--Boton follow-->\n")
        reseña.write("<a href=\"https://twitter.com/pelecolas?ref_src=twsrc%5Etfw\" " +
                     "class=\"twitter-follow-button\" data-show-count=\"false\">\n")
        reseña.write("Follow @pelecolas</a>\n" +
                     "<script async src=\"https://platform.twitter.com/widgets.js\"" +
                     "charset=\"utf-8\"></script>\n")
        reseña.write("\n<!--Boton compartir-->\n")
        reseña.write("<a href=\"https://twitter.com/share?ref_src=twsrc%5Etfw\" " +
                     "class=\"twitter-share-button\" data-show-count=\"false\">Tweet</a>\n" +
                     "<script async src=\"https://platform.twitter.com/widgets.js\"\n" +
                     "charset=\"utf-8\"></script>\n")

        reseña.close()

    def __write_header_data(self, file, text):
        file.write("<div style=\"text-align: right;\">\n")
        file.write("<span style=\"font-family: 'courier new', 'courier', monospace;\">" +
                   str(text) + "</span></div>\n")

    def __write_paragraph(self, file, parrafo):

        # Si todo el párrafo entero es una cita, lo alineo todo a la derecha
        # Compruebo si todo el párrafo son cursivas
        all_italic = self.__is_all_italic(parrafo)

        if not all_italic:
            # Formato para un párrafo normal
            file.write(
                "<div style=\"margin: 16px 0px; text-align: justify; text-indent: 21.25pt;\">\n")
            file.write(
                "<span style=\"font-family: 'times new roman', serif; margin: 0px;\">\n")
        else:
            # Formato para un párrafo que es íntegro una cita
            file.write(
                "<div class=\"MsoNormalCxSpMiddle\" style=\"text-align: right;\">\n")
            file.write(
                "<span style=\"font-family: 'times new roman', serif;\">\n")
        file.write(str(parrafo))
        file.write("\n</span></div>\n")

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


if __name__ == "__main__":
    Documento = html()
    Documento.write_html()
