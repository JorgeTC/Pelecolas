from src.gui import DlgScrollBase

from .list_title_mgr import TitleMgr


class DlgScrollTitles(DlgScrollBase):

    def __init__(self, question: str, title_list: list[str]):
        DlgScrollBase.__init__(self, question)

        # Objeto para buscar si el título que ha pedido el usuario
        # está entre los títulos que me han dado.
        self.quisiste_decir = TitleMgr(title_list)

    def get_ans_body(self) -> str:
        # Función sobreescrita de la clase base
        while not self.ans:
            # Inicializo la variable antes de llamar a input
            self.curr_index = -1
            # Al llamar a input es cuando me espero que se utilicen las flechas
            self.ans = input(self.question)
            self.options = self.quisiste_decir.suggestions(self.ans)
            # Se ha introducido un título, compruebo que sea correcto
            self.ans = self.quisiste_decir.exact_key(self.ans)

        return self.ans
