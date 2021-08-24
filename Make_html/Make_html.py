import docx
import re
from .Pelicula import Pelicula
from .WordReader import WordReader
from pathlib import Path


class html():

    def __init__(self, folder):
        self.folder = folder
        # Abro el documento para leerlo
        self.doc = docx.Document(folder / "Películas.docx")

        self.parrafos_critica = []
        self.titulo = ""
        self.año = ""
        self.duración = ""

        # Hago una lista con todos los títulos que tienen una crítica escrita
        reader = WordReader(folder)
        reader.list_titles()
        self.titulos = reader.titulos

        # Para el buscador de películas, defino los caracteres para los que no quiero que sea sensitivo
        self.__unwanted_chars = self.__make_unwanted_chars()

    def ask_for_data(self):
        exists_given_title = False
        # Pido los datos de la película que voy a buscar
        while not exists_given_title:
            self.titulo = input("Introduzca título de la película: ")
            exists_given_title = self.exists(self.titulo)

        self.director = input("Introduzca director: ")
        # Si en vez de un director se introduce la dirección de FA, no necesito nada más
        if not self.__interpretate_director():
            return

        self.año = input("Introduzca el año: ")
        self.duración = input("Introduzca duración de la película: ")

    def __make_unwanted_chars(self):

        # No quiero que los caracteres de puntuación afecten al buscar la película
        chars_dict = dict.fromkeys(map(ord, " ,!¡@#$?¿()."), None)
        # Elimino los tipos de tildes
        chars_dict.update(zip(map(ord, "áéíóú"),map(ord, "aeiou")))
        chars_dict.update(zip(map(ord, "àèìòù"),map(ord, "aeiou")))
        chars_dict.update(zip(map(ord, "âêîôû"),map(ord, "aeiou")))
        chars_dict.update(zip(map(ord, "äëïöü"),map(ord, "aeiou")))

        return chars_dict

    def __interpretate_director(self):
        # Si es un número, considero que se ha introducido un id de Filmaffinitty
        if self.director.isnumeric():
            url = 'https://www.filmaffinity.com/es/film' + self.director + '.html'
            return not self.__get_data_from_FA(url)

        if self.director.find("filmaffinity") >= 0:
            # Se ha introducido directamente la url
            return not self.__get_data_from_FA(self.director)

        else:
            # El director de la película es lo introducido por teclado
            return True

    def __get_data_from_FA(self, url):
        peli = Pelicula(urlFA=url)
        if not peli.exists:
            return False
        peli.GetDirectorYearDuration()
        self.director = peli.director
        self.año = peli.año
        self.duración = peli.duración
        return True

    def exists(self,titulo):
        # No quiero que sea sensible a las mayúsculas
        titulo = titulo.lower()

        for val in self.titulos:
            if titulo == val.lower():
                # Caso de coincidencia exacta
                self.titulo = val
                return True

        # Si es posible, siguiero los títulos más cercanos al introducido
        self.__closest_title(titulo)

        return False

    def __closest_title(self, titulo):
        # Intento buscar los casos más cercanos
        titulo = self.__normalize_string(titulo)
        found = False
        # Recorro la lista de titulos
        for iter in self.titulos:
            # Efectúo la comparación usando un título normalizado
            iter_ = self.__normalize_string(iter)
            # Busco si se contienen mutuamente
            if titulo.find(iter_) >= 0 or iter_.find(titulo) >= 0:
                # Hay suficiente concordancia como para sugerir el título
                if not found:
                    # Aún no he impreso nada por pantalla
                    print("Quizás quisiste decir...")
                    found = True
                # Imprimo el título original. El que se ha leído en el documento
                print(iter)

    def __normalize_string(self, str):
        # Elimino las mayúsculas
        str = str.lower()
        # Elimino espacios, signos de puntuación y acentos
        str = str.translate(self.__unwanted_chars)
        # Elimino caracteres repetidos
        str = re.sub(r'(.)\1+', r'\1', str)
        return str

    @staticmethod
    def __fin_de_parrafo(text):
        return text == "" or text == "\t"

    def search_film(self):
        # Si no tengo los datos de la película, los pido
        if not self.titulo:
            self.ask_for_data()
        # Empiezo a recorrer los párrafos desde el que sé que inicia la crítica que busco
        for paragraph in self.doc.paragraphs[self.titulos[self.titulo]:]:

            if self.__fin_de_parrafo(paragraph.text):
                # He llegado al final de la crítica. Dejo de leer el documento
                return self.parrafos_critica
            # Inicializo el párrafo
            parr_text = ""

            for run in paragraph.runs:
                # Conservo las cursivas
                if run.italic:
                    parr_text += "<i>" + run.text + "</i>"
                else:
                    parr_text += run.text

            if not self.parrafos_critica:
                # Si es el primer párrafo, elimino el título
                parr_text = parr_text[len(self.titulo):]
                parr_text = parr_text.lstrip(": ")

            # Añado saltos de línea para un html más legible
            parr_text = parr_text.replace(". ", ".\n")
            # Añado el texto a la lista de párrafos
            self.parrafos_critica.append(parr_text)

        assert("No ha sido posible encontrar la reseña.")

    def write_html(self):

        self.search_film()

        sz_file_name = "Reseña " + str(self.titulo) + ".html"
        reseña = open(self.folder / sz_file_name, mode="w",encoding="utf-8")

        # Escribo el encabezado
        reseña.write("<!-- Encabezado -->\n")
        reseña.write("<div style=\"text-align: right;\">\n")
        reseña.write("<span style=\"font-family: &quot;courier new&quot; , &quot;courier&quot; , monospace;\">Dir.: " + str(self.director) + "</span></div>\n")
        reseña.write("<div style=\"text-align: right;\">\n")
        reseña.write("<span style=\"font-family: &quot;courier new&quot; , &quot;courier&quot; , monospace;\">" + str(self.año) + "</span></div>\n")
        reseña.write("<div style=\"text-align: right;\">\n")
        reseña.write("<span style=\"font-family: &quot;courier new&quot; , &quot;courier&quot; , monospace;\">" + str(self.duración) + " min.</span></div>\n")

        # Iteramos los párrafos
        reseña.write("\n<!-- Párrafos -->\n")
        for parrafo in self.parrafos_critica:
            reseña.write("<div style=\"margin: 16px 0px; text-align: justify; text-indent: 21.25pt;\">\n")
            reseña.write("<span style=\"font-family: &quot;times new roman&quot; , serif; margin: 0px;\">\n")
            reseña.write(str(parrafo))
            reseña.write("\n</span></div>\n")

        # Escribo los botones de Twitter
        reseña.write("\n<!--Boton follow-->\n")
        reseña.write("<a href=\"https://twitter.com/pelecolas?ref_src=twsrc%5Etfw\" class=\"twitter-follow-button\" data-show-count=\"false\">\n")
        reseña.write("Follow @pelecolas</a><script async src=\"https://platform.twitter.com/widgets.js\" charset=\"utf-8\"></script>\n")
        reseña.write("\n<!--Boton compartir-->\n")
        reseña.write("<a href=\"https://twitter.com/share?ref_src=twsrc%5Etfw\" class=\"twitter-share-button\" data-show-count=\"false\">Tweet</a><script async src=\"https://platform.twitter.com/widgets.js\" charset=\"utf-8\"></script>\n")

        reseña.close()

if __name__ == "__main__":
    Documento = html()
    Documento.write_html()
