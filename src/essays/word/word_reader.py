from pathlib import Path
from typing import Iterator

import docx
from docx.text.paragraph import Paragraph

from src.config import Config, Param, Section

from .word_folder_mgr import WordFolderMgr

SEPARATOR_YEAR = " - "


def get_bold_title(paragraph: Paragraph) -> str:
    # Obtengo el primer fragamento de texto que esté en negrita.
    titulo = ""

    for run in paragraph.runs:
        # Conservo las negritas
        if not run.bold:
            # he llegado al final del título
            break
        titulo += run.text

    return titulo


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
    if text in ('', "\t", "\n"):
        return True

    # Es un párrafo y no un salto de línea
    return False


def init_paragraphs(year_parr: dict[int, int], paragraphs: list[Paragraph]):
    # Itero todos los docx que he encontrado
    for word in WordFolderMgr.SZ_ALL_DOCX:
        # Obtengo el año actual
        try:
            year = int(word.stem.split(SEPARATOR_YEAR)[1])
        except IndexError:
            year = 2017
        # Guardo en qué párrafo empieza el año actual
        year_parr[year] = len(paragraphs)
        # Añado los párrafos del docx actual
        # Evito añadir el primero, donde está el título del documento
        paragraphs.extend(docx.Document(word).paragraphs[1:])


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
    titulo = get_title(paragraph)
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


def init_titles(header: str, paragraphs: list[Paragraph], titulos: dict[str, int]) -> None:
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


class WordReader:
    # Me quedo con el nombre del archivo sin la extensión.
    HEADER = str(WordFolderMgr.SZ_ALL_DOCX[0].stem).split(SEPARATOR_YEAR)[0]
    # Me guardo sólo los párrafos, es lo que voy a iterar más adelante
    PARAGRAPHS: list[Paragraph] = []
    # Guardo a qué párrafo corresponde cada año
    YEARS_PARR: dict[int, int] = {}
    init_paragraphs(YEARS_PARR, PARAGRAPHS)
    # Lista con todos los títulos que encuentre.
    TITULOS: dict[str, int] = {}
    init_titles(HEADER, PARAGRAPHS, TITULOS)

    @classmethod
    def list_titles(self) -> list[str]:
        return list(self.TITULOS.keys())

    @classmethod
    def iter_review(cls, title: str) -> Iterator[Paragraph]:
        # Obtengo la posición donde empieza la reseña que busco
        first_parr: int = cls.TITULOS.get(title, -1)
        if first_parr == -1:
            return

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
                   output_path: Path = Config.get_folder_path(
                       Section.COUNT_FILMS, Param.TITLE_LIST_PATH),
                   b_index: bool = Config.get_bool(
                       Section.COUNT_FILMS, Param.ADD_INDEX),
                   b_year: bool = Config.get_bool(Section.COUNT_FILMS, Param.ADD_YEAR)) -> None:

        # Abro el documento txt para escribirlo
        titulos_doc = open(output_path / "Titulos de reseñas.txt", "w",
                           encoding='utf-8')

        next_years = iter(cls.YEARS_PARR.keys())
        # Cojo el primero de los años que hay que iterar
        next_year = next(next_years, None)

        for index, titulo in enumerate(cls.TITULOS):

            # Escritura del año
            # Compruebo que el título actual esté en una posición superior a donde inicia el siguiente año.
            # No me espero el caso de igualdad ya que ese párrafo corresponde al título del Word: peliculas.
            if b_year and cls.TITULOS[titulo] > cls.YEARS_PARR[next_year]:
                # Escribo el año en el documento
                titulos_doc.write("***" + str(next_year) + "***\n")
                # Avanzo al siguiente año
                past_year = next_year
                next_year = next(next_years, past_year)
                # Si es el último año, dejo de escribir años
                if next_year == past_year:
                    b_year = False

            # Si tengo que añadir el índice cojo el número y añado un espacio
            if b_index:
                titulos_doc.write(f"{index + 1} ")

            titulos_doc.write(f"{titulo}\n")

        # cierro el documento
        titulos_doc.close()
