import re
from dataclasses import dataclass
from pathlib import Path

from bs4 import BeautifulSoup

from src.aux_title_str import trim_year
from src.config import Config, Param, Section
from src.gui import DlgScrollBase
from src.html.make_html import SZ_HTML_FILE
from src.read_blog import BlogHiddenData


def get_title_from_html(html_path: Path) -> str:
    # Devuelve el nombre del archivo sin la palabra Reseña y la extensión
    regular_expresion = re.search('Reseña (.+).html', html_path.name)
    # Obtengo lo que haya después de la palabra reseña y antes de la extensión
    name = regular_expresion.group(1)
    return name


@dataclass(frozen=True)
class PostInfo:
    title: str
    content: str
    labels: str


class ContentMgr:

    DIR = Config.get_folder_path(Section.HTML, Param.OUTPUT_PATH_HTML)

    @classmethod
    def extract_html(cls, file_name: str) -> PostInfo:
        with open(cls.DIR / file_name, 'r', encoding="utf-8") as res:
            # Obtengo en una única string todo lo que voy a publicar
            content = res.read()
            # Extraigo de las notas del post el nombre de la película y las etiquetas
            parsed = BeautifulSoup(content, 'lxml')
            title = BlogHiddenData.TITLE.get(parsed)
            title = trim_year(title)
            labels = BlogHiddenData.LABELS.get(parsed)

        return PostInfo(title=title.upper(),
                        content=content,
                        labels=labels)

    @classmethod
    def get_content(cls) -> PostInfo:
        # Abro el diálogo para obtener el título entre los html que hay
        dlg = DlgScrollBase(question="Elija una reseña disponible: ",
                            options=cls.available_titles())
        choice = dlg.get_ans()
        # Teniendo el título, extraigo los datos del html
        return cls.extract_html(SZ_HTML_FILE(choice))

    @classmethod
    def available_titles(cls) -> list[str]:
        return [get_title_from_html(i) for i in list(cls.DIR.glob('*.html'))]
