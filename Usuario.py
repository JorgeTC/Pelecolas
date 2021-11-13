from pathlib import Path
from .dlg_scroll_base import DlgScrollBase
from .dlg_config import CONFIG
import ast

class Usuario(object):

    SZ_QUESTION = "Se van a importar los datos de {}\nEspero enter..."

    def __init__(self):
        self.ids = self.read_dict()
        self.nombre = CONFIG.get_value(CONFIG.S_READDATA, CONFIG.P_DEFAULT_USER)
        self.id = 0

        self.ask_user()

    def read_dict(self):

        sz_curr_folder = Path(__file__).resolve().parent
        sz_curr_folder = sz_curr_folder / "Readdata"
        sz_json = sz_curr_folder / "usuarios.json"

        file = open(sz_json, "r")
        contents = file.read()
        dictionary = ast.literal_eval(contents)

        file.close()

        return dictionary

    def ask_user(self):
        asker = DlgScrollBase(question=self.SZ_QUESTION.format(self.nombre),
                                options=list(self.ids.keys()),
                                empty_ans=True)
        # Pido el nombre del usuario cuyos datos se quieren importar
        nombre = asker.get_ans()
        # Si no se ha introducido nada por teclado, utilizo el nombre default.
        if nombre:
            self.nombre = nombre

        # Sé que el diálogo me ha dado un usuario válido, estará en el diccionario
        self.id = self.ids[self.nombre]

        # Guardo la última elección del usuario en el ini
        CONFIG.set_value(CONFIG.S_READDATA, CONFIG.P_DEFAULT_USER, self.nombre)
