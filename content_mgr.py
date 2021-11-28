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

    def __get_labels(self, parr):
        # Compruebo que sea un comentario
        # de lo contrario no tengo las etiquetas escritas en el documento
        if parr.find("<!--") < 0:
            return ""

        # Efectivamente la última linea es un comentario
        # limpio el comentario
        parr = parr[len("<!--"):-len("-->")]

        return parr

    def extract_html(self, title):
        # Obtengo el nombre del archivo html
        file_name = SZ_HTML_FILE(title)
        with open(self.dir / file_name, 'r', encoding="utf-8") as res:
            # Obtengo en una única string todo lo que voy a publicar
            content = res.read()
            # Leo en la última línea las etiquetas que acompañan a la reseña
            lines = content.splitlines()
            labels = self.__get_labels(lines[-1])

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
        return self.extract_html(choice)
