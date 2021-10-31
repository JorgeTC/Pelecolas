import keyboard
import sys

class YesNo():
    def __init__(self, question) -> None:
        self.__question = question
        self.__opciones = ["Sí", "No"]
        self.__index = 1

    def get_ans(self):
        # Todas las flechas me servirán para moverme
        keyboard.add_hotkey('up arrow', self.__scroll_up)
        keyboard.add_hotkey('left arrow', self.__scroll_up)
        keyboard.add_hotkey('down arrow', self.__scroll_up)
        keyboard.add_hotkey('right arrow', self.__scroll_up)

        ans = input(self.__question)
        ans = (ans == "Sí")

        # Cancelo la funcionalidad de las hotkeys
        keyboard.unhook_all()

        return ans

    def __scroll_up(self):
        self.__clear_written()
        self.__index = (self.__index + 1) % len(self.__opciones)
        keyboard.write( self.__opciones[self.__index])

    def __clear_written(self):
        # Al pulsar las teclas, también se está navegando entre los últimos inputs de teclado
        # Hago que se expliciten en la consola para poder borrarlos
        sys.stdout.flush()
        # Borro lo que haya escrito para que no lo detecte el input
        keyboard.send('esc')
