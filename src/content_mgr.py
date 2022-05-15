import re
from pathlib import Path

from bs4 import BeautifulSoup

from src.aux_title_str import split_title_year
from src.config import Config, Section, Param
from src.dlg_scroll_base import DlgScrollBase
from src.make_html import SZ_HTML_FILE
from src.read_blog import BlogHiddenData


def get_title_from_html(html_path: Path) -> str:
    # Quito la palabra reseña y la extensión
    return get_title_from_html_name(html_path.name)


def get_title_from_html_name(html_name: str) -> str:
    regular_expresion = re.search('Reseña (.+).html', html_name)
    # Obtengo lo que haya después de la palabra reseña y antes de la extensión
    name = regular_expresion.group(1)
    # Quito el posible año
    _, title = split_title_year(name)

    return title



class ContentMgr():

    DIR = Config.get_folder_path(Section.HTML, Param.OUTPUT_PATH_HTML)

    @classmethod
    def extract_html(cls, file_name: str) -> dict[str, str]:
        with open(cls.DIR / file_name, 'r', encoding="utf-8") as res:
            # Obtengo en una única string todo lo que voy a publicar
            content = res.read()
            # Extraigo de las notas del post el nombre de la película y las etiquetas
            parsed = BeautifulSoup(content, 'html.parser')
            title = BlogHiddenData.TITLE.get(parsed)
            _, title = split_title_year(title)
            labels = BlogHiddenData.LABELS.get(parsed)

        # Devuelvo la información en un diccionario
        post_info = {
            'title': title.upper(),
            'content': content,
            'labels': labels
        }

        return post_info

    @classmethod
    def get_content(cls) -> dict[str, str]:
        # Abro el diálogo para obtener el título entre los html que hay
        dlg = DlgScrollBase(question="Elija una reseña disponible: ",
                            options=cls.available_titles())
        choice = dlg.get_ans()
        # Teniendo el título, extraigo los datos del html
        return cls.extract_html(SZ_HTML_FILE(choice))

    @classmethod
    def available_titles(cls) -> list[str]:
        return [get_title_from_html(i) for i in list(cls.DIR.glob('*.html'))]
