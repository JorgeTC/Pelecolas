import ast

from src.aux_res_directory import get_res_folder
from src.config import Config, Param, Section
from src.gui.dlg_scroll_base import DlgScrollBase


def load_users_id() -> dict[str, int]:
    sz_json = get_res_folder("Readdata", "usuarios.json")

    with open(sz_json, "r") as file:
        contents = file.read()
        dictionary = ast.literal_eval(contents)
    return dictionary


class UserFA:

    SZ_QUESTION = "Se van a importar los datos de {}\nEspero enter...".format
    DEFAULT_USER = Config.get_value(Section.READDATA, Param.DEFAULT_USER)
    IDS = load_users_id()

    def __init__(self, name: str, id: int):
        self.name: str = name
        self.id: int = id

    @classmethod
    def ask_user(cls) -> 'UserFA':

        asker = DlgScrollBase(question=cls.SZ_QUESTION(cls.DEFAULT_USER),
                              options=list(cls.IDS.keys()),
                              empty_ans=True)
        # Pido el nombre del usuario cuyos datos se quieren importar
        name = asker.get_ans()
        # Si no se ha introducido nada por teclado, utilizo el nombre default.
        name = name or cls.DEFAULT_USER

        # Sé que el diálogo me ha dado un usuario válido, estará en el diccionario
        user_id = cls.IDS[name]

        # Guardo la última elección del usuario en el ini
        Config.set_value(Section.READDATA, Param.DEFAULT_USER, name)

        return UserFA(name, user_id)
