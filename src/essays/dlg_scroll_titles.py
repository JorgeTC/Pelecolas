from prompt_toolkit import prompt

from src.gui import DlgCompleter, DlgScrollBase

from .list_title_mgr import TitleMgr


class DlgScrollTitles(DlgScrollBase):

    def __init__(self, question: str, title_list: list[str]):
        DlgScrollBase.__init__(self, question, title_list)

        # Objeto para buscar si el título que ha pedido el usuario
        # está entre los títulos que me han dado.
        self.quisiste_decir = TitleMgr(self.options)

    def get_ans_body(self) -> str:
        # Función sobreescrita de la clase base
        while not self.ans:
            # Al llamar a input es cuando me espero que se utilicen las flechas
            self.ans = prompt(self.question,
                              completer=DlgCompleter(self.quisiste_decir.suggestions))
            # Se ha introducido un título, compruebo que sea correcto
            self.ans = self.quisiste_decir.exact_key(self.ans)

        return self.ans
