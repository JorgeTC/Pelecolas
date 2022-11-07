from src.gui import DlgScrollBase
from src.list_title_mgr import TitleMgr


class DlgScrollTitles(DlgScrollBase):

    def __init__(self, question: str, title_list: list[str]):
        DlgScrollBase.__init__(self, question)

        # Objeto para buscar si el título que ha pedido el usuario
        # está entre los títulos que me han dado.
        self.quisiste_decir = TitleMgr(title_list)

    def get_ans_body(self) -> str:
        # Función sobreescrita de la clase base
        while not self.sz_ans:
            # Inicializo las variables antes de llamar a input
            self.curr_index = -1
            self.sz_options = self.quisiste_decir.get_suggestions()
            self.n_options = len(self.sz_options)
            # Al llamar a input es cuando me espero que se utilicen las flechas
            self.sz_ans = input(self.sz_question)
            # Se ha introducido un título, compruebo que sea correcto
            self.sz_ans = self.quisiste_decir.exact_key(self.sz_ans)

        return self.sz_ans
