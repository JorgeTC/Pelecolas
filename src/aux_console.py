import sys

import win32gui as wg

# Memorizo la dirección de la consola
CURRENT_CONSOLE = wg.GetForegroundWindow()


def is_console_on_focus() -> bool:
    # Devuelvo si la ventana en foco actual es la consola
    return wg.GetForegroundWindow() == CURRENT_CONSOLE


def clear_current_line() -> None:
    # Borro todo el contenido de la linea actual y
    # me llevo el cursor al inicio de la linea
    sys.stdout.write('\r\033[2K\r')
    sys.stdout.flush()


def go_to_upper_row() -> None:
    sys.stdout.write('\033[A')


def delete_line() -> None:
    # Elimino todos los caracteres de la linea actual
    clear_current_line()
    # Subo al final de la línea anterior
    go_to_upper_row()
