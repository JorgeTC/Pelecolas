from functools import wraps
from threading import Lock
from typing import Callable

from .gui import ConsoleEvent


class DlgScrollBase(ConsoleEvent):

    keyboard_listen = Lock()

    def __init__(self, question: str = "", options: list[str] = None,
                 empty_option: bool = True, empty_ans: bool = False):
        ConsoleEvent.__init__(self)

        # Pregunta que voy a mostrar en pantalla
        self.question = question
        # Opciones sobre las que hacer scroll
        self.options = [] if options is None else options

        # Si después del último elemento de la iteración se mostrará una string vacía
        self.SCROLL_EMPTY_OPTION = empty_option
        self.min_index = -1 if self.SCROLL_EMPTY_OPTION else 0

        # Si tolero una respuesta vacía
        self.ALLOW_EMPTY_ANS = empty_ans
        # Variable para guardar la respuesta
        self.ans = ""

        # Índice que me dice cuál ha sido la última opción escrita
        self.curr_index = self.min_index

    def execute(self) -> str:
        ans = self.get_ans_body()

        # Indico que ya he conseguido la respuesta
        self.locker.release()

        return ans

    def get_ans_body(self) -> str:
        self.ans = ""
        # Función para sobrescribir.
        # Es la que hace la petición efectiva de un elemento de la lista
        while not self.ans:
            # Inicializo las variables antes de llamar a input
            self.curr_index = self.min_index
            # Al llamar a input es cuando me espero que se utilicen las flechas
            self.ans = input(self.question)
            if not self.ans and self.ALLOW_EMPTY_ANS:
                return self.ans
            # Se ha introducido un título, compruebo que sea correcto
            self.ans = self.ans if self.ans in self.options else ''

        return self.ans

    @staticmethod
    def hotkey_method(fn: Callable[['DlgScrollBase'], None]):
        @wraps(fn)
        def wrap(self: 'DlgScrollBase'):
            # Compruebo que no se esté ejecutando otra hotkey
            if self.keyboard_listen.locked():
                return

            # Inicio la ejecución de esta hotkey, evito que se ejecuten otras
            # Cuando termine la función, vuelvo a escuchar al teclado
            with self.keyboard_listen:
                fn(self)

        return wrap

    def __scroll(self, iter_fun: Callable[[int], int]):
        # si no tengo ninguna sugerencia, no puedo recorrer nada
        if not self.options:
            return

        clear_written()
        self.curr_index = iter_fun(self.curr_index)

        # Si el índice corresponde a un elemento de la lista, lo escribo
        if (self.curr_index != -1):
            curr_suggested = self.options[self.curr_index]

    @hotkey_method
    def __scroll_up(self) -> None:
        self.__scroll(self.__prev_index)

    @hotkey_method
    def __scroll_down(self) -> None:
        self.__scroll(self.__next_index)

    def __next_index(self, current_index: int) -> int:
        # Compruebo si puedo aumentar mi posición en la lista
        if current_index + 1 < len(self.options):
            # Puedo aumentar en la lista
            return current_index + 1
        else:
            # Doy la vuelta a la lista, empiezo por -1 si existe opción vacía
            # Empiezo por 0 si no existe opción vacía
            return self.min_index

    def __prev_index(self, current_index: int) -> int:
        # Compruebo si el índice es demasiado bajo (-1 o 0)
        if current_index <= self.min_index:
            # Le doy la última posición en la lista
            return len(self.options) - 1
        else:
            # Puedo bajar una posición en la lista
            return current_index - 1

    def get_ans(self):
        ConsoleEvent.execute_if_main_thread(self)
        with self.locker:
            return self.ans


def clear_written():
    ...
