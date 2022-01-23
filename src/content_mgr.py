from pathlib import Path
import re

from src.dlg_scroll_base import DlgScrollBase
from src.make_html import SZ_HTML_FILE
from src.aux_title_str import split_title_year


class ContentMgr():
    def __init__(self, folder:Path):
        self.dir = folder
        self.htmls = list(self.dir.glob('*.html'))

        # Me guardo los títulos para ofrecerlos en el diálogo
        self.titles = [self.__get_title_from_html(i) for i in self.htmls]

    def __get_title_from_html(self, html_path):
        # Quito la palabra reseña y la extensión
        return self.__get_title_from_html_name(html_path.name)

    def __get_title_from_html_name(self, html_name):
        regular_expresion = re.search('Reseña (.+).html', html_name)
        # Obtengo lo que haya después de la palabra reseña y antes de la extensión
        name = regular_expresion.group(1)
        # Quito el posible año
        _, title = split_title_year(name)

        return title

    def __get_labels(self, parr):
        # Buscador de comentarios
        # El resultado no tendrá trailing spaces,
        # el grupo que hemos definido termina en una coma.
        search_comment = re.compile(r'<!-- *(.*,) *-->')
        try:
            return search_comment.match(parr).group(1)
        except AttributeError:
            # Excepción que salta si no hay ninguna coincidencia con la re
            return ""

    def extract_html(self, file_name):
        with open(self.dir / file_name, 'r', encoding="utf-8") as res:
            # Obtengo en una única string todo lo que voy a publicar
            content = res.read()
            # Leo en la última línea las etiquetas que acompañan a la reseña
            lines = content.splitlines()
            labels = self.__get_labels(lines[-1])

        # Devuelvo la información en un diccionario
        post_info = {
            'title' : self.__get_title_from_html_name(file_name).upper(),
            'content' : content,
            'labels' : labels
        }

        return post_info

    def get_content(self):
        # Abro el diálogo para obtener el título entre los html que hay
        dlg = DlgScrollBase(question="Elija una reseña disponible:",
                            options=self.titles)
        choice = dlg.get_ans()
        # Teniendo el título, extraigo los datos del html
        return self.extract_html(SZ_HTML_FILE(choice))
