from configparser import ConfigParser
from pathlib import Path
from tkinter import Tk, filedialog

from src.aux_res_directory import get_res_folder
from src.dlg_scroll_base import DlgScrollBase

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
    S_COUNT_FILMS = "CONTAR"
    S_POST = "POST"
    S_DRIVE = "DRIVE"

    # Html
    P_FILTER_PUBLISHED = "Filter_published"
    P_SCRAP_BLOG = "Force_bog_scraping"
    P_ADD_STYLE = "Write_style"
    P_OUTPUT_PATH_HTML = "Path_output_html"
    P_YES_ALWAYS_DIR = "New_confidence_director"
    # Readdata
    P_FILTER_FA = "Filter_FilmAffinity"
    P_DEFAULT_USER = "Mem_user_FA"
    P_OUTPUT_EXCEL = "Path_output_excel"
    # Count films
    P_ADD_YEAR = "Add_year"
    P_ADD_INDEX = "Add_index"
    P_WORD_FOLDER = "Folder_with_words"
    P_TITLE_LIST_PATH = "Output_folder_count"
    # Post
    P_BLOG_ID = "Blog_id"
    P_DATE = "Posting_date"
    P_TIME = "Posting_time"
    P_AS_DRAFT = "As_draft"
    # Drive
    P_FOLDER_ID = "Drive_folder_to_update_id"
    P_PDF_PATH = "Pdf_folder"

    def __init__(self):
        super().__init__(question="", options=[], empty_option=True, empty_ans=True)
        # Abro el lector del archivo
        self.config = ConfigParser()
        # Dirección del ini
        self.sz_path = get_res_folder(SZ_FILE)
        self.config.read(self.sz_path, encoding="utf-8")

        # Qué estoy configurando actualmente
        self.__curr_section = ""
        self.__curr_param = ""

        self.fill_default_values()

    def save_config(self):
        with open(self.sz_path, 'w', encoding="utf-8") as configfile:
            self.config.write(configfile)

    def fill_default_values(self):
        # Configuraciones para html
        self.add_default_value(self.S_HTML, self.P_FILTER_PUBLISHED, False)
        self.add_default_value(self.S_HTML, self.P_SCRAP_BLOG, False)
        self.add_default_value(self.S_HTML, self.P_ADD_STYLE, False)
        self.add_default_value(self.S_HTML, self.P_OUTPUT_PATH_HTML, 'auto')
        self.add_default_value(self.S_HTML, self.P_YES_ALWAYS_DIR, "")
        # Configuraciones para readdata
        self.add_default_value(self.S_READDATA, self.P_FILTER_FA, 1)
        self.add_default_value(self.S_READDATA, self.P_DEFAULT_USER, 'Jorge')
        self.add_default_value(self.S_READDATA, self.P_OUTPUT_EXCEL, 'auto')
        # Configuraciones para escribir el txt
        self.add_default_value(self.S_COUNT_FILMS, self.P_ADD_YEAR, False)
        self.add_default_value(self.S_COUNT_FILMS, self.P_ADD_INDEX, False)
        self.add_default_value(self.S_COUNT_FILMS, self.P_WORD_FOLDER, 'auto')
        self.add_default_value(self.S_COUNT_FILMS, self.P_TITLE_LIST_PATH, 'auto')
        # Configuraciones para post
        self.add_default_value(self.S_POST, self.P_BLOG_ID, '4259058779347983900')
        self.add_default_value(self.S_POST, self.P_DATE, 'auto')
        self.add_default_value(self.S_POST, self.P_TIME, '20:00')
        self.add_default_value(self.S_POST, self.P_AS_DRAFT, False)
        # Configuraciones para actualizar drive
        self.add_default_value(self.S_DRIVE, self.P_FOLDER_ID, '13UbwzbjVFQ8e_UaNalqm_iMihjBDBvtm')
        self.add_default_value(self.S_DRIVE, self.P_PDF_PATH, 'auto')

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
            self.__ask_param()
            self.print_section(self.__curr_section)
            self.__choose_param()
        else:
            self.__choose_section()

    def __ask_param(self):
        ans = input(SZ_NEW_VALUE.format(self.__curr_param))
        self.config.set(self.__curr_section, self.__curr_param, ans)

    def get_value(self, section: str, param: str) -> str:
        return self.config[section][param]

    def set_value(self, section: str, param: str, value) -> None:
        # Me espero que se introduzca un valor en una sección que existe
        if param not in self.config[section]:
            assert("{} no pertenece a la sección {}.".format(param, section))

        # Lo cambio en el objeto
        self.config.set(section, param, str(value))

        # Actualizo el archivo ini
        self.save_config()

    def get_int(self, section: str, param: str) -> int:
        return self.config.getint(section, param)

    def get_bool(self, section: str, param: str) -> bool:
        return self.config.getboolean(section, param)

    def get_folder_path(self, section: str, param: str) -> Path:
        # Leo lo que hya escrito en el ini
        ini_data = self.config[section][param]

        # Compruebo que sea una carpeta
        if not Path(ini_data).is_dir():
            # Si no es una carpeta válida, abro una ventana para elegirla
            Tk().withdraw()

            ini_data = filedialog.askdirectory(title=f"{section} {param}")
            # Guardo el dato elegido
            self.config.set(section, param, ini_data)

        return Path(ini_data)

    def get_file_path(self, section: str, param: str) -> Path:
        # Leo lo que hya escrito en el ini
        ini_data = self.config[section][param]

        # Compruebo que sea una carpeta
        if not Path(ini_data).is_file():
            # Si no es una carpeta válida, abro una ventana para elegirla
            Tk().withdraw()

            ini_data = filedialog.askopenfile(title=f"{section} {param}")
            # Guardo el dato elegido
            self.config.set(section, param, ini_data)

        return Path(ini_data)

    def print(self):
        for section in self.config.sections():
            self.print_section(section)

    def print_section(self, section):
        print(section.upper())
        for param in self.config[section]:
            print(SZ_PRINT_VALUE.format(param, self.config[section][param]))


CONFIG = DlgConfig()


def manage_config():
    # Importo los módulos de windows para comprobar el teclado
    import win32api
    import win32con

    # Comrpuebo si la tecla control está apretada
    if win32api.GetAsyncKeyState(win32con.VK_CONTROL) & 0x8000 > 0:
        # Abro el diálogo
        CONFIG.run()
        CONFIG.save_config()
