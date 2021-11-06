from .dlg_scroll_base import DlgScrollBase
import configparser

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
        self.config.read(SZ_FILE)

        # Qué estoy configurando actualmente
        self.__curr_section = ""
        self.__curr_param = ""

        self.fill_default_values()

    def __del__(self):
        with open(SZ_FILE, 'w') as configfile:
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
        self.sz_options = list(dict(self.config.items(self.__curr_section)).keys())
        self.n_options = len(self.sz_options)
        self.b_empty_option = True
        self.__curr_param = self.get_ans()

        if self.__curr_param:
            self.__set_param()
            self.__choose_param()
        else:
            self.__choose_section()

    def __set_param(self):
        ans = input(SZ_NEW_VALUE.format(self.__curr_param))
        self.config[self.__curr_section][self.__curr_param] = ans

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
