import keyboard
import sys

class DlgScrollBase():
    sz_question = ""
    sz_options = []
    b_empty_option = True
    __keyboard_listen = True
    sz_ans = ""

    def __init__(self, question="", options=[], empty_option=True):
        self.sz_question = question
        self.sz_options = options
        self.b_empty_option = empty_option

        if (self.b_empty_option):
            self.min_index = -1
        else:
            self.min_index = 0

        self.curr_index = self.min_index

    def get_ans(self):
        keyboard.add_hotkey('up arrow', self.__scroll_up)
        keyboard.add_hotkey('down arrow', self.__scroll_down)

        while not self.sz_ans:
            # Inicializo las variables antes de llamar a input
            self.curr_index = self.min_index
            # Al llamar a input es cuando me espero que se itilicen las flechas
            self.sz_ans = input(self.sz_question)
            # Se ha introducido un título, compruebo que sea correcto
            self.sz_ans = self.__check_ans(self.sz_ans)

        # Cancelo la funcionalidad de las hotkeys
        keyboard.unhook_all()

        return self.sz_ans

    def __scroll_up(self):

        if not self.__keyboard_listen:
            return
        self.__keyboard_listen = False

        # si no tengo ninguna sugerencia, no puedo recorrer nada
        if not len(self.sz_options):
            self.__keyboard_listen = True
            return

        self.__clear_written()
        # Compruebo si el índice es demasiado bajo (-1 o 0)
        if (self.curr_index < self.min_index):
            # Le doy la última posición en la lista
            self.curr_index = len(self.sz_options) - 1
        else:
            # Puedo bajar una posición el título
            self.curr_index = self.curr_index - 1

        # Si el índice corresponde a un título, lo escribo
        if (self.curr_index != -1):
            curr_suggested = self.__get_option_by_index()
            keyboard.write(curr_suggested)

        self.__keyboard_listen = True

    def __get_option_by_index(self):
        return self.sz_options[self.curr_index]

    def __scroll_down(self):

        if not self.__keyboard_listen:
            return
        self.__keyboard_listen = False

        # si no tengo ninguna sugerencia, no puedo recorrer nada
        if not len(self.sz_options):
            self.__keyboard_listen = True
            return

        self.__clear_written()
        # Compruebo si puedo aumentar mi posición en la lista
        if (self.curr_index < len(self.sz_options) - 1):
            # Puedo aumentar en la lista
            self.curr_index = self.curr_index + 1
        else:
            # Doy la vuelta a la lista, empiezo por -1 si existe opción vacía
            # Empiezo por 0 si no existe opción vacía
            self.curr_index = self.min_index

        # Si el índice corresponde a un título, lo escribo
        if (self.curr_index != -1):
            curr_suggested = self.__get_option_by_index()
            keyboard.write(curr_suggested)

        self.__keyboard_listen = True

    def __clear_written(self):
        # Al pulsar las teclas, también se está navegando entre los últimos inputs de teclado
        # Hago que se expliciten en la consola para poder borrarlos
        sys.stdout.flush()
        # Borro lo que haya escrito para que no lo detecte el input
        keyboard.send('esc')

    def __check_ans(self, ans):
        if ans in self.sz_options:
            return ans
        else:
            return ""

