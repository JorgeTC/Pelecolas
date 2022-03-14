import os

import win32gui as wg

# Memorizo la dirección de la consola
CURRENT_CONSOLE = wg.GetForegroundWindow()


def is_console_on_focus() -> bool:
    # Devuelvo si la ventana en foco actual es la consola
    return wg.GetForegroundWindow() == CURRENT_CONSOLE


def clear_current_line() -> None:
    # Me desplazo al inicio de la fila actual
    # Imprimo tantos espacios como ancho tenga la consola
    # Evito que se imprima un espacio
    print("\r" + " " * os.get_terminal_size().columns, end="")


def go_to_upper_row() -> None:
    print("\033[A", end="")


def delete_line() -> None:
    # Elimino todos los caracteres de la linea actual
    clear_current_line()
    # Subo al final de la línea anterior
    go_to_upper_row()
