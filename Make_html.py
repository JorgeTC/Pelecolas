import docx
from .Pelicula import Pelicula
from .WordReader import WordReader
from .searcher import Searcher
from .list_title_mgr import TitleMgr


class html():

    def __init__(self, folder):
        self.folder = folder
        # Abro el documento para leerlo
        self.doc = docx.Document(folder / "Películas.docx")

        self.parrafos_critica = []
        self.titulo = ""
        self.año = ""
        self.duración = ""
        self.director = ""

        # Hago un diccionario con todos los títulos que tienen una crítica escrita
        reader = WordReader(folder)
        reader.list_titles()
        self.titulos = reader.titulos

        # Objeto para buscar si el título que ha pedido el usuario
        # está disponible en el archivo word.
        self.quisiste_decir = TitleMgr( list(self.titulos.keys()) )


    def ask_for_data(self):

        # Pido los datos de la película que voy a buscar
        while not self.titulo:
            self.titulo = input("Introduzca título de la película: ")
            self.titulo = self.quisiste_decir.exact_key(self.titulo)

        # Trato de buscar información de esta película en FA.
        FA = Searcher(self.titulo)
        FA.print_state()

        while not self.director:
            self.director = input("Introduzca director: ")
            # Si en vez de un director se introduce la dirección de FA, no necesito nada más
            if not self.__interpretate_director(FA.get_url()):
                return

        self.año = input("Introduzca el año: ")
        self.duración = input("Introduzca duración de la película: ")

    def __interpretate_director(self, suggested_url):

        # Caso en el que no se ha introducido nada.
        # Busco la ficha automáticamente.
        if not self.director:
            if suggested_url and self.__get_data_from_FA(suggested_url):
                # Lo introducido no es un director.
                # Considero que no necesito más información.
                return False

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
        peli.get_parsed_page()

        if not peli.exists():
            return False

        peli.get_director()
        self.director = peli.director
        peli.get_año()
        self.año = peli.año
        peli.get_duracion()
        self.duración = peli.duracion
        return True


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
