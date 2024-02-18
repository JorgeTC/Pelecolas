import re
from io import StringIO
from itertools import chain, islice, takewhile
from pathlib import Path
from typing import Iterator, TextIO

import docx
from docx.text.paragraph import Paragraph
from docx.text.run import Run

from src.config import Config, Param, Section

from .word_folder_mgr import WordFolderMgr

DOCUMENT_NAME = re.compile(r"(?P<header>.*) - (?P<year>\d{4})")


class IllFormedBold(ValueError):
    '''Raise when cannot tell whether a paragraph starts by bold or not.'''


def is_run_bold(index: int, run: Run) -> bool:
    # Si el inicio de párrafo no tiene indicado el estado de la negrita,
    # lo considero un error
    if run.bold == None and index == 0:
        error_msg = f"Could not resolve bold status for: {run.text}"
        raise IllFormedBold(error_msg)

    return bool(run.bold)


def get_bold_title(paragraph: Paragraph) -> str:
    # Obtengo el primer fragamento de texto que esté en negrita.
    titulo = StringIO()

    # Conservo las negritas
    indexed_runs = enumerate(paragraph.runs)
    for _, run in takewhile(lambda i_run: is_run_bold(*i_run), indexed_runs):
        titulo.write(run.text)

    return titulo.getvalue()


def get_title(paragraph: Paragraph) -> str:

    # Obtengo lo que esté en negrita
    title = get_bold_title(paragraph)

    # Compruebo que lo que he leído sea un título.
    # Busco que su separador sean dos puntos.
    # Elimino los espacios que fueren delante del separador.
    title = title.strip(" ")
    # Compruebo que esté presente el separador.
    if not title or title[-1] != ":":
        title = ""
    else:
        # Ya he usado los dos puntos para reconocer el título.
        # Ahora los puedo eliminar para tener limpio el título.
        title = title.strip(": ")

    return title


def is_break_line(text: str) -> bool:

    # Limpio de espacios el texto
    text = text.strip()

    # Compruebo que contenga un salto de linea
    if text in {'', "\t", "\n"}:
        return True

    # Es un párrafo y no un salto de línea
    return False


def init_paragraphs(word_documents: list[Path]):
    year_parr: dict[int, int] = {}
    paragraphs: list[Paragraph] = []
    # Itero todos los docx que he encontrado
    for word in word_documents:
        # Obtengo el año actual
        try:
            year = int(DOCUMENT_NAME.search(word.stem).group('year'))
        except (AttributeError, TypeError):
            year = 2017
        # Guardo en qué párrafo empieza el año actual
        year_parr[year] = len(paragraphs)
        # Añado los párrafos del docx actual
        # Evito añadir el primero, donde está el título del documento
        paragraphs.extend(docx.Document(word).paragraphs[1:])

    return paragraphs, year_parr


def has_next_parr_title(text: str, header: str) -> bool:
    if text == header:
        # No cuento el encabezado del documento
        return False
    if is_break_line(text):
        # Si hay un doble salto de párrafo, quizás ha terminado una crítica
        # El inicio del siguiente párrafo será el título de la película
        return True

    return False


def append_title(paragraph: Paragraph, index: int, titulos: dict[str, int]) -> bool:
    # Leo el posible título de este párrafo.
    try:
        titulo = get_title(paragraph)
    except IllFormedBold:
        print(f"No pude determinar si '{paragraph.text}' contiene un título")
        return False

    # Si no se ha encontrado título, no es el inicio de una crítica.
    if not titulo:
        # No he conseguido añadir nada.
        return False

    if titulo not in titulos:
        # En este punto ya sabemos que tenemos un título
        titulos[titulo] = index
    else:
        # Si el título ya está recogido, aviso al usuario de que está mal escrito el Word
        print(f"Repeated title {titulo}")

    # He añadido un título.
    return True


def init_titles(header: str, paragraphs: list[Paragraph]) -> dict[str, int]:
    titulos: dict[str, int] = {}

    # inicializo la variable.
    # No quiero buscar desde el principio porque sé que encontraré el título del documento.
    search_title = False

    # Recorro todos los párrafos del documento
    for i, paragraph in enumerate(paragraphs):
        if not search_title:
            # Compruebo si el próximo párrafo podría tener un título.
            search_title = has_next_parr_title(paragraph.text, header)
        else:
            # Probablemente estoy en un párrafo que es el primero de una crítica.
            # Si he añadido un título, no me espero que el siguiente párrafo comience con título.
            # Si no he añadido nada, sigo buscando.
            search_title = not append_title(paragraph, i, titulos)

    return titulos


class WordReader:
    # Me quedo con el nombre del archivo sin la extensión.
    HEADER = re.search(DOCUMENT_NAME,
                       WordFolderMgr.SZ_ALL_DOCX[0].stem).group('header')
    # Me guardo sólo los párrafos, es lo que voy a iterar más adelante
    # Guardo a qué párrafo corresponde cada año
    PARAGRAPHS, YEARS_PARR = init_paragraphs(WordFolderMgr.SZ_ALL_DOCX)
    # Lista con todos los títulos que encuentre.
    TITULOS = init_titles(HEADER, PARAGRAPHS)

    @classmethod
    def list_titles(self) -> list[str]:
        return list(self.TITULOS.keys())

    @classmethod
    def iter_review(cls, title: str) -> Iterator[Paragraph]:
        # Obtengo la posición donde empieza la reseña que busco
        first_parr = cls.TITULOS[title]

        # Voy devolviendo los párrafos de la reseña
        for paragraph in cls.PARAGRAPHS[first_parr:]:
            # He llegado al final de la crítica. Dejo de leer el documento
            if is_break_line(paragraph.text):
                return
            yield paragraph

        # He llegado al final del documento sin encontrar salto de línea
        return

    @classmethod
    def write_list(cls, *,
                   output_path: Path = Config.get_folder_path(Section.COUNT_FILMS,
                                                              Param.TITLE_LIST_PATH),
                   write_index: bool = Config.get_bool(Section.COUNT_FILMS,
                                                       Param.ADD_INDEX),
                   write_year: bool = Config.get_bool(Section.COUNT_FILMS, Param.ADD_YEAR)) -> None:

        # Abro el documento txt para escribirlo
        with open(output_path / "Titulos de reseñas.txt", "w",
                  encoding='utf-8') as titles_doc:
            cls.write_file_list(titles_doc, write_index, write_year)

    @classmethod
    def write_file_list(cls, titles_doc: TextIO, write_index: bool, write_year: bool):

        next_years = iter(cls.YEARS_PARR.keys())
        # Cojo el primero de los años que hay que iterar
        next_year = next(next_years)

        for index, titulo in enumerate(cls.TITULOS):

            # Escritura del año
            # Compruebo que el título actual esté en una posición superior a donde inicia el siguiente año.
            # No me espero el caso de igualdad ya que ese párrafo corresponde al título del Word: peliculas.
            if write_year and cls.TITULOS[titulo] > cls.YEARS_PARR[next_year]:
                # Escribo el año en el documento
                titles_doc.write(f"***{next_year}***\n")
                # Avanzo al siguiente año
                try:
                    next_year = next(next_years)
                # Si es el último año, dejo de escribir años
                except StopIteration:
                    write_year = False

            # Si tengo que añadir el índice cojo el número y añado un espacio
            if write_index:
                titles_doc.write(f"{index + 1} ")

            titles_doc.write(f"{titulo}\n")

    @classmethod
    def find_year(cls, title_to_search: str) -> int:
        parr_index = WordReader.TITULOS[title_to_search]

        previous_years = takewhile(lambda dict_pair: dict_pair[1] <= parr_index,
                                   WordReader.YEARS_PARR.items())
        last_year, _ = last_element(previous_years)
        return last_year

    @classmethod
    def count_each_year(cls) -> dict[int, int]:

        # Guardo todos los párrafos que son el comienzo de una reseña
        title_indices_set = set(cls.TITULOS.values())

        # Creo el diccionario donde cuento cuántas reseñas tiene cada año
        titles_count_by_year = {}

        # Genero una lista con los ragos correspodientes a cada año
        start_indices = cls.YEARS_PARR.values()
        end_indices = chain(islice(cls.YEARS_PARR.values(), 1, None),
                            [len(cls.PARAGRAPHS)])
        ranges_list = [range(start_index, next_start_index)
                       for start_index, next_start_index in zip(start_indices, end_indices)]
        ranges_by_year = {year: year_range
                          for year, year_range in zip(cls.YEARS_PARR, ranges_list)}

        # Itero todos los años con el rango de párrafos que le corresponde
        for year, year_range in ranges_by_year.items():
            # Obtengo todos los párrafos de este año que son inicio de título
            title_indices_for_year = set(year_range) & title_indices_set
            # los cuento
            title_count = len(title_indices_for_year)

            # Guardo el resultado en el diccionario
            titles_count_by_year[year] = title_count

        return titles_count_by_year


def last_element(iterable):
    for element in iterable:
        pass
    return element
