import sys
from functools import wraps
from threading import Lock

import keyboard
from src.aux_console import is_console_on_focus
from src.gui.console_event import ConsoleEvent


class DlgScrollBase(ConsoleEvent):

    keyboard_listen = Lock()

    def __init__(self, question: str = "", options: list[str] = None,
                 empty_option: bool = True, empty_ans: bool = False):
        ConsoleEvent.__init__(self)

        # Pregunta que voy a mostrar en pantalla
        self.sz_question = question
        # Opciones sobre las que hacer scroll
        if options is None:
            self.sz_options = []
        else:
            self.sz_options = options
        self.n_options = len(self.sz_options)

        # Si después del último elemento de la iteración se mostrará una string vacía
        self.SCROLL_EMPTY_OPTION = empty_option
        if (self.SCROLL_EMPTY_OPTION):
            self.min_index = -1
        else:
            self.min_index = 0

        # Si tolero una respuesta vacía
        self.ALLOW_EMPTY_ANS = empty_ans
        # Variable para guardar la respuesta
        self.sz_ans = ""

        # Índice que me dice cuál ha sido la última opción escrita
        self.curr_index = self.min_index

    def execute(self) -> str:
        # Doy a las flechas las funciones para hacer scroll
        keyboard.add_hotkey('up arrow', self.__scroll_up)
        keyboard.add_hotkey('down arrow', self.__scroll_down)

        ans = self.get_ans_body()

        # Cancelo la funcionalidad de las hotkeys
        keyboard.unhook_all()

        # Indico que ya he conseguido la respuesta
        self.locker.release()

        return ans

    def get_ans_body(self) -> str:
        self.sz_ans = ""
        # Función para sobrescribir.
        # Es la que hace la petición efectiva de un elemento de la lista
        while not self.sz_ans:
            # Inicializo las variables antes de llamar a input
            self.curr_index = self.min_index
            # Al llamar a input es cuando me espero que se utilicen las flechas
            self.sz_ans = input(self.sz_question)
            if not self.sz_ans and self.ALLOW_EMPTY_ANS:
                return self.sz_ans
            # Se ha introducido un título, compruebo que sea correcto
            self.sz_ans = self.__check_ans(self.sz_ans)

        return self.sz_ans

    def hotkey_method(fn):
        @wraps(fn)
        def wrap(self: 'DlgScrollBase'):
            # Compruebo que la consola tenga el foco
            if not is_console_on_focus():
                return

            # Compruebo que no se esté ejecutando otra hotkey
            if self.keyboard_listen.locked():
                return

            # Inicio la ejecución de esta hotkey, evito que se ejecuten otras
            self.keyboard_listen.acquire()
            fn(self)
            # Ya he terminado la función, vuelvo a escuchar al teclado
            self.keyboard_listen.release()

        return wrap

    @hotkey_method
    def __scroll_up(self) -> None:

        # si no tengo ninguna sugerencia, no puedo recorrer nada
        if not self.n_options:
            return

        self.__clear_written()
        # Compruebo si el índice es demasiado bajo (-1 o 0)
        if (self.curr_index <= self.min_index):
            # Le doy la última posición en la lista
            self.curr_index = self.n_options - 1
        else:
            # Puedo bajar una posición en la lista
            self.curr_index = self.curr_index - 1

        # Si el índice corresponde a un elemento de la lista, lo escribo
        if (self.curr_index != -1):
            curr_suggested = self.__get_option_by_index()
            keyboard.write(curr_suggested)

    @hotkey_method
    def __scroll_down(self) -> None:

        # si no tengo ninguna sugerencia, no puedo recorrer nada
        if not self.n_options:
            return

        # Limpio la consola
        self.__clear_written()
        # Compruebo si puedo aumentar mi posición en la lista
        if (self.curr_index < self.n_options - 1):
            # Puedo aumentar en la lista
            self.curr_index = self.curr_index + 1
        else:
            # Doy la vuelta a la lista, empiezo por -1 si existe opción vacía
            # Empiezo por 0 si no existe opción vacía
            self.curr_index = self.min_index

        # Si el índice corresponde a un elemento de la lista, lo escribo
        if (self.curr_index != -1):
            curr_suggested = self.__get_option_by_index()
            keyboard.write(curr_suggested)

    def get_ans(self):
        ConsoleEvent.execute_if_main_thread(self)
        with self.locker:
            return self.sz_ans

    def __get_option_by_index(self) -> str:
        return self.sz_options[self.curr_index]

    def __clear_written(self):
        # Al pulsar las teclas, también se está navegando entre los últimos inputs de teclado
        # Hago que se expliciten en la consola para poder borrarlos
        sys.stdout.flush()
        # Borro lo que haya escrito para que no lo detecte el input
        keyboard.send('esc')

    def __check_ans(self, ans: str) -> str:
        # Compruebo si la respuesta está en la lista
        if ans in self.sz_options:
            return ans
        else:
            return ""
