from typing import Callable, Iterable

from prompt_toolkit import prompt
from prompt_toolkit.completion import CompleteEvent, Completer, Completion
from prompt_toolkit.document import Document

from .gui import ConsoleEvent

# Clase para pasar como argumento al llamar a `prompt`.
# A partir de lo que el usuario haya escrito, sugerirá entre las opciones disponibles.
class DlgCompleter(Completer):

    def __init__(self, matcher: Callable[[str], list[str]]):
        Completer.__init__(self)

        # Función que dado el input del usuario,
        # me sugiera una lista de posibles opciones de autocompletado
        self.matcher = matcher

    def get_completions(self, document: Document, event: CompleteEvent) -> Iterable[Completion]:
        # Obtengo todo lo que ha escrito el usuario
        user_input = document.text

        # Llamo a la función que me dará las opciones que debo sugerir
        # al usuario en base a lo que ha escrito hasta ahora
        options = self.matcher(user_input)

        # Devuelvo las opciones de completado.
        # El segundo argumento indica que al elegir una de las opciones,
        # se deberá sustituir completamente lo que el usuario haya escrito.
        return (Completion(option, -len(user_input)) for option in options)


# Clase para pasar como argumento al llamar a `prompt`.
# Independientemente de lo que el usuario haya escrito siempre sugeriré la misma lista de opciones.
class ScrollCompleter(DlgCompleter):

    def __init__(self, options: list[str]):
        # Guardo las opciones que tengo que sugerir al usuario
        self.options = options.copy()
        # La función matcher recibirá el string que haya escrito el usuario
        # Siempre devolverá la lista de opciones que le hemos pasado
        DlgCompleter.__init__(self, lambda _: self.options)


# Clase para que el usuario escriba un input entre varias opciones disponibles.
# Se le mostrarán las opciones para que tenga posibilidad de autocompletar.
# El método `get_ans` devolverá siempre una de las opciones.
class DlgScrollBase(ConsoleEvent):

    def __init__(self, question: str, options: list[str],
                 empty_ans: bool = False):
        ConsoleEvent.__init__(self)

        # Pregunta que voy a mostrar en pantalla
        self.question = question
        # Opciones sobre las que hacer scroll
        self.options = options

        # Si tolero una respuesta vacía
        self.ALLOW_EMPTY_ANS = empty_ans
        # Variable para guardar la respuesta
        self.ans = ""

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
            self.ans = prompt(self.question,
                              completer=ScrollCompleter(self.options))
            # Si se ha introducido una cadena vacía y eso es una opción válida, salgo de la función
            if not self.ans and self.ALLOW_EMPTY_ANS:
                return self.ans
            # El usuario ha escrito una string no vacía, compruebo que sea una de las opciones válidas
            self.ans = self.ans if self.ans in self.options else ''

        return self.ans

    def get_ans(self):
        ConsoleEvent.execute_if_main_thread(self)
        with self.locker:
            return self.ans
