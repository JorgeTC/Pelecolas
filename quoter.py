import csv

from .blog_csv_mgr import BlogCsvMgr
from .blog_scraper import BlogScraper


class Quoter(BlogCsvMgr):
    INI_QUOTE_CHAR = "“"
    FIN_QUOTE_CHAR = "”"

    OPEN_LINK = "<a href=\"{}\">"
    CLOSE_LINK = "</a>"

    def __init__(self) -> None:
        # Necesito el csv, así que lo escribo
        scraper = BlogScraper()
        if self.is_needed():
            scraper.write_csv()

        # Guardo las citaciones que vaya sugeriendo
        self.__directors = []
        self.__titles = []

        # Texto que estoy estudiando actualmente
        self.__ori_text = ""
        # Película actual.
        # No quiero citarme a mi mismo
        self.titulo = ""

        # Lector de csv
        self.__csv_file = open(self.sz_csv_file, encoding=self.ENCODING)
        self.__csv_reader = csv.reader(self.__csv_file, delimiter=",")
        self.__csv_reader = list(self.__csv_reader)

    def quote_parr(self, text):
        # Guardo el párrafo recién introducido
        self.__ori_text = text

        self.__quote_titles()
        self.__quote_directors()
        return self.__ori_text

    def __quote_titles(self):
        # Cuento cuántas comillas hay
        self.__ini_comillas_pos = find(self.__ori_text, self.INI_QUOTE_CHAR)
        self.__fin_comillas_pos = find(self.__ori_text, self.FIN_QUOTE_CHAR)
        if len(self.__ini_comillas_pos) != len(self.__fin_comillas_pos):
            assert("Comillas impares, no se citará este párrafo")
            return

        # Construyo una lista con todas las posibles citas
        posible_titles = []
        for i, j in zip(self.__ini_comillas_pos, self.__fin_comillas_pos):
            posible_titles.append(self.__ori_text[i + 1:j])

        for title in posible_titles:
            row = self.__row_in_csv(title)
            # La película no está indexada
            if row > 0:
                # Si la película ya está citada, no la cito otra vez
                if title not in self.__titles and title != self.titulo:
                    self.__titles.append(title)
                    self.__add_post_link(row)
            # Elimino los índices que ya he usado
            self.__ini_comillas_pos.pop(0)
            self.__fin_comillas_pos.pop(0)

    def __add_post_link(self, row):
        # Construyo el html para el enlace
        ini_link = self.OPEN_LINK.format(self.__csv_reader[row][1])
        # La posición dentro de mi texto me la indica
        # el primer elemento de las listas de índices
        position = self.__ini_comillas_pos[0] + 1
        self.__ori_text = insert_string_in_position(
            self.__ori_text, ini_link, position)
        # Actualizo la posición del cierre de las comillas
        position = self.__fin_comillas_pos[0] + len(ini_link)
        self.__ori_text = insert_string_in_position(
            self.__ori_text, self.CLOSE_LINK, position)

        # Actualizo todo el resto de índices
        delta = len(ini_link) + len(self.CLOSE_LINK)
        self.__ini_comillas_pos = [i + delta for i in self.__ini_comillas_pos]
        self.__fin_comillas_pos = [i + delta for i in self.__fin_comillas_pos]

    def __quote_directors(self):
        pass

    def __row_in_csv(self, title: str):
        for index, row in enumerate(self.__csv_reader):
            if title.lower() == row[0].lower().strip("\""):
                return index

        # No lo hemos encontrado
        return -1


def find(s, ch):
    return [i for i, ltr in enumerate(s) if ltr == ch]


def insert_string_in_position(sr, sub, pos):
    return sr[:pos] + sub + sr[pos:]
