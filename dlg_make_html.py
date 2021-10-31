import keyboard
import sys
from .list_title_mgr import TitleMgr
from .Pelicula import Pelicula
from .searcher import Searcher


class DlgHtml():

    # Mensajes para pedir información
    ASK_TITLE = "Introduzca título de la película: "
    ASK_DIRECTOR = "Introduzca director: "
    ASK_YEAR = "Introduzca el año: "
    ASK_DURATION = "Introduzca duración de la película: "

    def __init__(self, title_list) -> None:
        # Objeto para buscar si el título que ha pedido el usuario
        # está disponible en el archivo word.
        self.quisiste_decir = TitleMgr(title_list)

        # Valores que debo devolver para el objeto html
        # titulo, año, director, duración
        # Los guardo todos en un objeto Pelicula
        self.data = Pelicula()

    def ask_for_data(self):
        # Pido los datos de la película que voy a buscar
        # Titulo
        self.__ask_for_title()

        # Trato de buscar información de esta película en FA.
        FA = Searcher(self.data.titulo)
        FA.print_state()

        while not self.data.director:
            self.data.director = input(self.ASK_DIRECTOR)
            # Si en vez de un director se introduce la dirección de FA, no necesito nada más
            if not self.__interpretate_director(FA.get_url()):
                return

        self.data.año = input(self.ASK_YEAR)
        self.data.duracion = input(self.ASK_DURATION)

    def __interpretate_director(self, suggested_url):

        # Caso en el que no se ha introducido nada.
        # Busco la ficha automáticamente.
        if not self.data.director:
            if suggested_url and self.__get_data_from_FA(suggested_url):
                # Lo introducido no es un director.
                # Considero que no necesito más información.
                return False

        # Si es un número, considero que se ha introducido un id de Filmaffinitty
        if self.data.director.isnumeric():
            url = 'https://www.filmaffinity.com/es/film' + self.data.director + '.html'
            return not self.__get_data_from_FA(url)

        if self.data.director.find("filmaffinity") >= 0:
            # Se ha introducido directamente la url
            return not self.__get_data_from_FA(self.director)

        else:
            # El director de la película es lo introducido por teclado
            return True

    def __get_data_from_FA(self, url):
        # No quiero que se modifique el título que tengo leído.
        # El actual lo he oebtenido del word,
        # Pelicula me puede dar un título de FA que no sea idéntico al que hay en el word
        ori_title = self.data.titulo

        self.data = Pelicula(urlFA=url)
        self.data.get_parsed_page()

        if not self.data.exists():
            return False

        self.data.titulo = ori_title
        self.data.get_director()
        self.data.get_año()
        self.data.get_duracion()
        return True

    def __ask_for_title(self):
        # Quiero que las flechas de arriba y abajo me sirvan para iterar la lista de títulos sugeridos
        # Las hago variables de la clase para poder acceder a ellas desde las hotkey
        self.__curr_index = -1
        self.__keyboard_listen = True
        self.__list_size = 0

        # Escribo la funcionalidad de las flechas para poder recorrer las sugerencias
        keyboard.add_hotkey('up arrow', self.__on_up_key)
        keyboard.add_hotkey('down arrow', self.__on_down_key)

        while not self.data.titulo:
            # Inicializo las variables antes de llamar a input
            self.__curr_index = -1
            self.__list_size = self.quisiste_decir.get_suggested_titles_count()
            # Al llamar a input es cuando me espero que se itilicen las flechas
            self.data.titulo = input(self.ASK_TITLE)
            # Se ha introducido un título, compruebo que sea correcto
            self.data.titulo = self.quisiste_decir.exact_key(self.data.titulo)

        # Cancelo la funcionalidad de las hotkeys
        keyboard.unhook_all()
        # Elimino las variables que me servían solo para esto
        del self.__curr_index
        del self.__keyboard_listen
        del self.__list_size

    def __on_up_key(self):

        if not self.__keyboard_listen:
            return
        self.__keyboard_listen = False

        # si no tengo ninguna sugerencia, no puedo recorrer nada
        if not self.__list_size:
            self.__keyboard_listen = True
            return

        self.__clear_written()
        # Compruebo si el índice es demasiado bajo (-1)
        if (self.__curr_index < 0):
            # Le doy la última posición en la lista
            self.__curr_index = self.__list_size - 1
        else:
            # Puedo bajar una posición el título
            self.__curr_index = self.__curr_index - 1

        # Si el índice corresponde a un título, lo escribo
        if (self.__curr_index != -1):
            curr_suggested = self.quisiste_decir.get_suggested_title(
                self.__curr_index)
            keyboard.write(curr_suggested)

        self.__keyboard_listen = True

    def __on_down_key(self):

        if not self.__keyboard_listen:
            return
        self.__keyboard_listen = False

        # si no tengo ninguna sugerencia, no puedo recorrer nada
        if not self.__list_size:
            self.__keyboard_listen = True
            return

        self.__clear_written()
        # Compruebo si puedo aumentar mi posición en la lista
        if (self.__curr_index < self.__list_size - 1):
            # Puedo aumentar en la lista
            self.__curr_index = self.__curr_index + 1
        else:
            # Doy la vuelta a la lista, empiezo por -1
            self.__curr_index = - 1

        # Si el índice corresponde a un título, lo escribo
        if (self.__curr_index != -1):
            curr_suggested = self.quisiste_decir.get_suggested_title(
                self.__curr_index)
            keyboard.write(curr_suggested)

        self.__keyboard_listen = True

    def __clear_written(self):
        # Al pulsar las teclas, también se está navegando entre los últimos inputs de teclado
        # Hago que se expliciten en la consola para poder borrarlos
        sys.stdout.flush()
        # Borro lo que haya escrito para que no lo detecte el input
        keyboard.send('esc')