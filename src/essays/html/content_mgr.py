import re
from pathlib import Path

from bs4 import BeautifulSoup

from src.config import Config, Param, Section
from src.gui import DlgScrollBase

from ..aux_title_str import trim_year
from ..blog_scraper import BlogHiddenData
from ..google_api import Post
from .make_html import HTML_FILE


def get_title_from_html(html_path: Path) -> str:
    # Devuelve el nombre del archivo sin la palabra Reseña y la extensión
    regular_expresion = re.search('Reseña (.+).html', html_path.name)
    # Obtengo lo que haya después de la palabra reseña y antes de la extensión
    name = regular_expresion.group(1)
    return name


class ContentMgr:

    DIR = Config.get_folder_path(Section.HTML, Param.OUTPUT_PATH_HTML)

    @classmethod
    def extract_html(cls, file_name: str) -> Post:
        with open(cls.DIR / file_name, 'r', encoding="utf-8") as res:
            # Obtengo en una única string todo lo que voy a publicar
            content = res.read()
            # Extraigo de las notas del post el nombre de la película y las etiquetas
            parsed = BeautifulSoup(content, 'lxml')
            title = BlogHiddenData.TITLE.get(parsed)
            title = trim_year(title)
            labels = BlogHiddenData.LABELS.get(parsed)

        return Post(title=title.upper(),
                    content=content,
                    labels=labels)

    @classmethod
    def get_content(cls) -> Post:
        # Abro el diálogo para obtener el título entre los html que hay
        dlg = DlgScrollBase(question="Elija una reseña disponible: ",
                            options=cls.available_titles())
        choice = dlg.get_ans()
        # Teniendo el título, extraigo los datos del html
        return cls.extract_html(HTML_FILE(choice))

    @classmethod
    def available_titles(cls) -> list[str]:
        return [get_title_from_html(i) for i in cls.DIR.glob('*.html')]
