from pathlib import Path
from Make_html import SZ_HTML_FILE
from dlg_scroll_base import DlgScrollBase


class ContentMgr():
    def __init__(self, folder:Path):
        self.dir = folder
        self.htmls = list(self.dir.glob('*.html'))

        # Me guardo los títulos para ofrecerlos en el diálogo
        self.titles = [self.__get_title_from_html(i) for i in self.htmls]

    def __get_title_from_html(self, html_path):
        # Quito la palabra reseña y la extensión
        return html_path.name[len('Reseña '):-len('.html')]

    def __get_title_from_index(self, html_index):
        return self.__get_title_from_html(self.htmls[html_index])

    def get_title_and_content(self):

        dlg = DlgScrollBase(question="Elija una reseña disponible:",
                            options=self.titles)
        choice = dlg.get_ans()
        file_name = SZ_HTML_FILE(choice)
        with open(self.dir / file_name, 'r', encoding="utf-8") as res:
            content = res.read()

        return (choice.upper(), content)
