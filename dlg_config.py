import configparser
import time
from pathlib import Path

import keyboard

from .dlg_scroll_base import DlgScrollBase

SZ_FILE = "General.ini"

SZ_SECTIONS = "Secciones: "
SZ_PARÁMETROS = "Parámetros: "
SZ_NEW_VALUE = "Nuevo valor de {}: "

SZ_WELCOME = "## BIENVENIDO A LA CONFIGURACIÓN ##"
SZ_CLOSE = "### SALIENDO DE LA CONFIGURACIÓN ##"
SZ_PRINT_VALUE = "  {}: {}"


class DlgConfig(DlgScrollBase):

    S_HTML = "HTML"
    S_READDATA = "READDATA"

    P_FILTER_PUBLISHED = "Filter published"
    P_FILTER_FA = "Filter FilmAffinity"

    def __init__(self):
        super().__init__(question="", options=[], empty_option=True, empty_ans=True)
        # Abro el lector del archivo
        self.config = configparser.ConfigParser()
        # Abro el archivo
        self.sz_path = Path(__file__).resolve().parent / SZ_FILE
        self.config.read(self.sz_path)

        # Qué estoy configurando actualmente
        self.__curr_section = ""
        self.__curr_param = ""

        self.fill_default_values()

    def __del__(self):
        with open(self.sz_path, 'w') as configfile:
            self.config.write(configfile)

    def fill_default_values(self):
        # Configuraciones para html
        self.add_default_value(self.S_HTML, self.P_FILTER_PUBLISHED, False)
        # Configuraciones para readdata
        self.add_default_value(self.S_READDATA, self.P_FILTER_FA, 1)
        pass

    def add_default_value(self, section, param, value):
        # Si no existe la sección, la añado
        if section not in self.config:
            self.config.add_section(section)
        # Si no existe el parámetro lo añado con el valor default
        if param not in self.config[section]:
            self.config.set(section, param, str(value))

    def run(self):
        print(SZ_WELCOME)
        self.print()
        self.__choose_section()
        print(SZ_CLOSE)

    def __choose_section(self):
        # Me muevo hasta la sección que sea menester
        self.sz_question = SZ_SECTIONS
        self.sz_options = self.config.sections()
        self.n_options = len(self.sz_options)
        self.b_empty_option = True
        self.__curr_section = self.get_ans()

        if self.__curr_section:
            self.__choose_param()

    def __choose_param(self):
        # Me muevo hasta la sección que sea menester
        self.sz_question = SZ_PARÁMETROS
        self.sz_options = list(
            dict(self.config.items(self.__curr_section)).keys())
        self.n_options = len(self.sz_options)
        self.b_empty_option = True
        self.__curr_param = self.get_ans()

        if self.__curr_param:
            self.__set_param()
            self.print_section(self.__curr_section)
            self.__choose_param()
        else:
            self.__choose_section()

    def __set_param(self):
        ans = input(SZ_NEW_VALUE.format(self.__curr_param))
        self.config.set(self.__curr_section, self.__curr_param, ans)

    def get_value(self, section, param):
        return self.config[section][param]

    def get_bool(self, section, param):
        return self.config.getboolean(section, param)

    def print(self):
        for section in self.config.sections():
            self.print_section(section)

    def print_section(self, section):
        print(section.upper())
        for param in self.config[section]:
            print(SZ_PRINT_VALUE.format(param, self.config[section][param]))


# Variable que me dice si el menú se ha abierto o no
MENU_OPEN = False


def manage_config():
    # Gestión para abrir el menú si se inicia el programa pulsando control

    def on_ctrl():
        # Si está pulsada la tecla control, abro el menú

        # Establezco que el menú ha sido abierto
        global MENU_OPEN
        MENU_OPEN = True
        # Evito que se pueda seguir escuhando al teclado.
        # Debo hacerlo antes de abrir el manú porque
        # tiene sus propios eventos de teclado.
        keyboard.unhook_all()
        # Abro el diálogo
        config = DlgConfig()
        config.run()
        del config

    # Asocio el evento con la tecla control
    keyboard.add_hotkey('ctrl', on_ctrl())
    # Espero para que llegue el evento
    time.sleep(0.1)
    # Compruebo si se ha abierto el menú
    global MENU_OPEN
    if not MENU_OPEN:
        # Si no se ha abierto, ya ha pasado el tiempo.
        # No doy más oportunidad a que se vuelva a abrir.
        keyboard.unhook_all()
