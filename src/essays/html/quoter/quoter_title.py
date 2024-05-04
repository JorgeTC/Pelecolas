from contextlib import suppress
from typing import NamedTuple

from ... import word as Word
from ...aux_title_str import split_title_year, trim_year
from .quoter_base import QuoterBase, find, insert_string_in_position


class FilmCitation(NamedTuple):
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
            title_in_csv = QuoterBase.csv_content.get()[row].title
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
    url = QuoterBase.csv_content.get()[row].link
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
                    for index, row in enumerate(QuoterBase.csv_content.get())
                    if title.lower() == row.title.lower().strip("\""))
    except StopIteration:
        raise ValueError


def row_in_csv_year_insensitive(title: str) -> int:
    # Comparo los títulos del word quitándoles el año
    matches_but_year = [word_title
                        for word_title in Word.LIST_TITLES
                        if title.lower() == trim_year(word_title.lower())]
    # Si la coincidencia es única, miro que lo que he encontrado esté presente en el CSV
    if len(matches_but_year) != 1:
        raise ValueError
    return row_in_csv(matches_but_year[0])


def row_in_csv_missing_year_in_word(title: str, year: str) -> int:
    # Hago la búsqueda sin atender al año
    row_index = row_in_csv_year_insensitive(title)

    # Compruebo que el título coincidente sea del año correcto
    year_in_csv = QuoterBase.csv_content.get()[row_index].year
    if year != year_in_csv:
        raise ValueError
    return row_index


def find_row_in_csv(title: str) -> int:
    with suppress(ValueError):
        # Busco la fila del csv con coincidencia exacta
        return row_in_csv(title)

    # Compruebo si el año ha sido la causa por la que no he encontrado el título
    year, only_title = split_title_year(title)
    if not year:
        # Si el título no incluye año, busco si existe una película cuyo título coincida
        return row_in_csv_year_insensitive(only_title)
    else:
        # Si el título no incluye año, busco si existe una película de ese año cuyo título coincida
        return row_in_csv_missing_year_in_word(only_title, year)
