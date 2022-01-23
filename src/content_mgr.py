from pathlib import Path
import re

from bs4 import BeautifulSoup

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

    def extract_html(self, file_name):
        with open(self.dir / file_name, 'r', encoding="utf-8") as res:
            # Obtengo en una única string todo lo que voy a publicar
            content = res.read()
            # Extraigo de las notas del post el nombre de la película y las etiquetas
            parsed = BeautifulSoup(content, 'html.parser')
            title = parsed.find(id='film-title')['value']
            labels = parsed.find(id='post-labels')['value']

        # Devuelvo la información en un diccionario
        post_info = {
            'title' : title.upper(),
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
