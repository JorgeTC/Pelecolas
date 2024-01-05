from contextlib import suppress
from dataclasses import dataclass

from ... import word as Word
from ...aux_title_str import trim_year
from ..blog_csv_mgr import CSV_COLUMN
from .quoter_base import QuoterBase, find, insert_string_in_position


@dataclass
class FilmCitation:
    begin: int
    end: int
    title: str


class QuoterTitle:

    def __init__(self, titulo: str) -> None:
        self.titulo = titulo
        self._quoted_titles: set[str] = set()

    def quote_titles(self, text: str) -> str:
        # Cuento cuántas comillas hay
        ini_comillas_pos = find(text, QuoterBase.INI_QUOTE_CHAR)
        fin_comillas_pos = find(text, QuoterBase.FIN_QUOTE_CHAR)
        if len(ini_comillas_pos) != len(fin_comillas_pos):
            assert ("Comillas impares, no se citará este párrafo")
            return text

        # Construyo una lista con todas las posibles citas
        posible_titles = [FilmCitation(begin=begin,
                                       end=end,
                                       title=text[begin + 1:end])
                          for begin, end in zip(ini_comillas_pos, fin_comillas_pos)]

        for title in reversed(posible_titles):
            try:
                row = find_row_in_csv(title.title)
            # La película no está indexada
            except ValueError:
                continue
            # Guardo el título como viene escrito en el CSV
            title_in_csv = QuoterBase.CSV_CONTENT[row][CSV_COLUMN.TITLE]
            # Si la película ya está citada, no la cito otra vez
            if title_in_csv in self._quoted_titles:
                continue
            # Si la cita es la película actual, no añado link
            if title_in_csv == self.titulo:
                continue
            # Guardo este título como ya citado
            self._quoted_titles.add(title_in_csv)
            text = add_post_link(text, title, row)

        return text


def add_post_link(text: str, citation: FilmCitation, row: int) -> str:
    # Construyo el html para el enlace
    url = QuoterBase.CSV_CONTENT[row][CSV_COLUMN.LINK]
    ini_link = QuoterBase.OPEN_LINK(url)

    # Escribo el cierre del link
    position = citation.end
    text = insert_string_in_position(text, QuoterBase.CLOSE_LINK,
                                     position)

    # Escribo el inicio del link
    position = citation.begin + 1
    text = insert_string_in_position(text, ini_link,
                                     position)

    return text


def row_in_csv(title: str) -> int:
    try:
        return next(index
                    for index, row in enumerate(QuoterBase.CSV_CONTENT)
                    if title.lower() == row[CSV_COLUMN.TITLE].lower().strip("\""))
    except StopIteration:
        raise ValueError


def find_row_in_csv(title: str) -> int:
    with suppress(ValueError):
        # Busco la fila del csv con coincidencia exacta
        return row_in_csv(title)

    # Busco cuántos títulos del Word coinciden salvo el año
    matches_but_year = [word_title
                        for word_title in Word.LIST_TITLES
                        if title.lower() == trim_year(word_title.lower())]
    # Si la coincidencia es única, miro que lo que he encontrado esté presente en el CSV
    if len(matches_but_year) != 1:
        raise ValueError
    return row_in_csv(matches_but_year[0])
