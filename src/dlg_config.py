from configparser import ConfigParser
import enum
from pathlib import Path

from src.aux_res_directory import get_res_folder
from src.dlg_scroll_base import DlgScrollBase

SZ_FILE = "General.ini"

SZ_SECTIONS = "Secciones: "
SZ_PARÁMETROS = "Parámetros: "
SZ_NEW_VALUE = "Nuevo valor de {}: "

SZ_WELCOME = "## BIENVENIDO A LA CONFIGURACIÓN ##"
SZ_CLOSE = "### SALIENDO DE LA CONFIGURACIÓN ##"
SZ_PRINT_VALUE = "  {}: {}"


class Section(enum.Enum):
    HTML = "HTML"
    READDATA = "READDATA"
    COUNT_FILMS = "CONTAR"
    POST = "POST"
    DRIVE = "DRIVE"


class Param(enum.Enum):
    # Html
    FILTER_PUBLISHED = "Filter_published"
    SCRAP_BLOG = "Force_bog_scraping"
    ADD_STYLE = "Write_style"
    OUTPUT_PATH_HTML = "Path_output_html"
    YES_ALWAYS_DIR = "New_confidence_director"
    # Readdata
    FILTER_FA = "Filter_FilmAffinity"
    DEFAULT_USER = "Mem_user_FA"
    OUTPUT_EXCEL = "Path_output_excel"
    # Count films
    ADD_YEAR = "Add_year"
    ADD_INDEX = "Add_index"
    WORD_FOLDER = "Folder_with_words"
    TITLE_LIST_PATH = "Output_folder_count"
    # Post
    BLOG_ID = "Blog_id"
    DATE = "Posting_date"
    TIME = "Posting_time"
    AS_DRAFT = "As_draft"
    # Drive
    FOLDER_ID = "Drive_folder_to_update_id"
    PDF_PATH = "Pdf_folder"


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
            self.__ask_param()
            self.print_section(self.__curr_section)
            self.__choose_param()
        else:
            self.__choose_section()

    def __ask_param(self):
        ans = input(SZ_NEW_VALUE.format(self.__curr_param))
        self.config.set(self.__curr_section, self.__curr_param, ans)

    def print(self):
        for section in self.config.sections():
            self.print_section(section)

    def print_section(self, section: str):
        print(section.upper())
        for param in self.config[section]:
            print(SZ_PRINT_VALUE.format(param, self.config[section][param]))


class Config:

    # Abro el lector del archivo
    config = ConfigParser()
    # Dirección del ini
    sz_path = get_res_folder(SZ_FILE)
    config.read(sz_path, encoding="utf-8")

    dlg_config = DlgConfig(config)

    @classmethod
    def save_config(cls):
        with open(cls.sz_path, 'w', encoding="utf-8") as configfile:
            cls.config.write(configfile)

    @classmethod
    def get_value(cls, section: str, param: str) -> str:
        return cls.config[section][param]

    @classmethod
    def get_int(cls, section: str, param: str) -> int:
        return cls.config.getint(section, param)

    @classmethod
    def get_bool(cls, section: str, param: str) -> bool:
        return cls.config.getboolean(section, param)

    @classmethod
    def get_folder_path(cls, section: str, param: str) -> Path:
        # Leo lo que hya escrito en el ini
        ini_data = cls.config[section][param]

        # Compruebo que sea una carpeta
        while not Path(ini_data).is_dir():
            # Si no es una carpeta válida, la pido al usuario
            ini_data = input(
                f"Introducir path de la carpeta {section} {param}: ")
            # Guardo el dato elegido
            cls.set_value(section, param, ini_data)

        return Path(ini_data)

    @classmethod
    def get_file_path(cls, section: str, param: str) -> Path:
        # Leo lo que hya escrito en el ini
        ini_data = cls.config[section][param]

        # Compruebo que sea una carpeta
        while not Path(ini_data).is_file():
            # Si no es una carpeta válida, la pido al usuario
            ini_data = input(
                f"Introducir path del archivo {section} {param}: ")
            # Guardo el dato elegido
            cls.set_value(section, param, ini_data)

        return Path(ini_data)

    @classmethod
    def fill_default_values(cls):
        # Configuraciones para html
        cls.add_default_value(Section.HTML, Param.FILTER_PUBLISHED, False)
        cls.add_default_value(Section.HTML, Param.SCRAP_BLOG, False)
        cls.add_default_value(Section.HTML, Param.ADD_STYLE, False)
        cls.add_default_value(Section.HTML, Param.OUTPUT_PATH_HTML, 'auto')
        cls.add_default_value(Section.HTML, Param.YES_ALWAYS_DIR, "")
        # Configuraciones para readdata
        cls.add_default_value(Section.READDATA, Param.FILTER_FA, 1)
        cls.add_default_value(Section.READDATA, Param.DEFAULT_USER, 'Jorge')
        cls.add_default_value(Section.READDATA, Param.OUTPUT_EXCEL, 'auto')
        # Configuraciones para escribir el txt
        cls.add_default_value(Section.COUNT_FILMS, Param.ADD_YEAR, False)
        cls.add_default_value(Section.COUNT_FILMS, Param.ADD_INDEX, False)
        cls.add_default_value(Section.COUNT_FILMS, Param.WORD_FOLDER, 'auto')
        cls.add_default_value(Section.COUNT_FILMS,
                              Param.TITLE_LIST_PATH, 'auto')
        # Configuraciones para post
        cls.add_default_value(Section.POST, Param.BLOG_ID,
                              '4259058779347983900')
        cls.add_default_value(Section.POST, Param.DATE, 'auto')
        cls.add_default_value(Section.POST, Param.TIME, '20:00')
        cls.add_default_value(Section.POST, Param.AS_DRAFT, False)
        # Configuraciones para actualizar drive
        cls.add_default_value(Section.DRIVE, Param.FOLDER_ID,
                              '13UbwzbjVFQ8e_UaNalqm_iMihjBDBvtm')
        cls.add_default_value(Section.DRIVE, Param.PDF_PATH, 'auto')

    @classmethod
    def add_default_value(cls, section: Section, param: Param, value):
        # Si no existe la sección, la añado
        if str(section) not in cls.config:
            cls.config.add_section(section)
        # Si no existe el parámetro lo añado con el valor default
        if str(param) not in cls.config[section]:
            cls.config.set(section, param, str(value))

    fill_default_values()

    @classmethod
    def set_value(cls, section: str, param: str, value) -> None:
        # Me espero que se introduzca un valor en una sección que existe
        if param not in cls.config[section]:
            assert("{} no pertenece a la sección {}.".format(param, section))

        # Lo cambio en el objeto
        cls.config.set(section, param, str(value))

        # Actualizo el archivo ini
        cls.save_config()

    @classmethod
    def run_dlg(cls):
        cls.dlg_config.run()


def manage_config():
    # Importo los módulos de windows para comprobar el teclado
    import win32api
    import win32con

    # Comrpuebo si la tecla control está apretada
    if win32api.GetAsyncKeyState(win32con.VK_CONTROL) & 0x8000 > 0:
        # Abro el diálogo
        Config.run_dlg()
        Config.save_config()
