import keyboard
from .list_title_mgr import TitleMgr
from .Pelicula import Pelicula
from .searcher import Searcher


class DlgHtml():

    def __init__(self, title_list) -> None:
        # Objeto para buscar si el título que ha pedido el usuario
        # está disponible en el archivo word.
        self.quisiste_decir = TitleMgr(title_list)

        # Valores que debo devolver para el objeto html
        self.titulo = ""
        self.año = ""
        self.director = ""
        self.duración = ""

    def ask_for_data(self):
        # Pido los datos de la película que voy a buscar
        # Titulo
        self.__ask_for_title()

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

    def __ask_for_title(self):
        # Quiero que las flechas de arriba y abajo me sirvan para iterar la lista de títulos sugeridos
        self.curr_index = -1

        # Escribo la funcionalidad de las flechas para poder recorrer las sugerencias
        keyboard.add_hotkey('up arrow', self.__on_up_key)
        keyboard.add_hotkey('down arrow', self.__on_down_key)

        while not self.titulo:
            self.curr_index = -1
            self.titulo = input("Introduzca título de la película: ")
            self.titulo = self.quisiste_decir.exact_key(self.titulo)

        # Cancelo la funcionalidad de las hotkeys
        keyboard.unhook_all_hotkeys()
        del self.curr_index

    def __on_down_key(self):
        self.__clear_written()
        # Compruebo si el índice es demasiado bajo (-1)
        if (self.curr_index < 0):
            # Le doy la última posición en la lista
            self.curr_index = self.quisiste_decir.get_suggested_titles_count() - 1
        else:
            # Puedo bajar una posición el título
            self.curr_index = self.curr_index - 1

        # Si el índice corresponde a un título, lo escribo
        if (self.curr_index != -1):
            curr_suggested = self.quisiste_decir.get_suggested_title(
                self.curr_index)
            keyboard.write(curr_suggested)

    def __on_up_key(self):
        self.__clear_written()
        # Compruebo si puedo aumentar mi posición en la lista
        if (self.curr_index < self.quisiste_decir.get_suggested_titles_count()):
            # Puedo aumentar en la lista
            self.curr_index = self.curr_index + 1
        else:
            # Doy la vuelta a la lista, empiezo por -1
            self.curr_index = - 1

        # Si el índice corresponde a un título, lo escribo
        if (self.curr_index != -1):
            curr_suggested = self.quisiste_decir.get_suggested_title(
                self.curr_index)
            keyboard.write(curr_suggested)

    def __clear_written(self):
        for _ in range(70):
            keyboard.send('backspace')
