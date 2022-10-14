from configparser import ConfigParser

from src.gui import DlgScrollBase

SZ_SECTIONS = "Secciones: "
SZ_PARAMETROS = "Parámetros: "
SZ_NEW_VALUE = "Nuevo valor de {}: ".format

SZ_WELCOME = "## BIENVENIDO A LA CONFIGURACIÓN ##"
SZ_CLOSE = "### SALIENDO DE LA CONFIGURACIÓN ##"
SZ_PRINT_VALUE = "  {}: {}".format


class DlgConfig(DlgScrollBase):

    def __init__(self, config: ConfigParser):
        super().__init__(question="", options=[], empty_option=True, empty_ans=True)

        self.config = config

        # Qué estoy configurando actualmente
        self.__curr_section = ""
        self.__curr_param = ""

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
        self.SCROLL_EMPTY_OPTION = True
        self.__curr_section = self.get_ans()

        if self.__curr_section:
            self.__choose_param()

    def __choose_param(self):
        # Me muevo hasta la sección que sea menester
        self.sz_question = SZ_PARAMETROS
        self.sz_options = list(
            dict(self.config.items(self.__curr_section)).keys())
        self.n_options = len(self.sz_options)
        self.SCROLL_EMPTY_OPTION = True
        self.__curr_param = self.get_ans()

        if self.__curr_param:
            self.__ask_param()
            self.print_section(self.__curr_section)
            self.__choose_param()
        else:
            self.__choose_section()

    def __ask_param(self):
        ans = input(SZ_NEW_VALUE(self.__curr_param))
        self.config.set(self.__curr_section, self.__curr_param, ans)

    def print(self):
        for section in self.config.sections():
            self.print_section(section)

    def print_section(self, section: str):
        print(section.upper())
        for param in self.config[section]:
            print(SZ_PRINT_VALUE(param, self.config[section][param]))
