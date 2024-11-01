from contextlib import suppress
from enum import StrEnum
from typing import Iterator

from bs4 import BeautifulSoup

from .google_api import Post
from .list_title_mgr import TitleMgr
from .word import LIST_TITLES, WordReader


class BlogHiddenData(StrEnum):
    TITLE = "film-title"
    YEAR = "year"
    DIRECTOR = "director"
    COUNTRY = "pais"
    URL_FA = "link-FA"
    LABELS = "post-labels"
    DURATION = "duration"
    IMAGE = "link-image"

    def get(self, content: BeautifulSoup) -> str:
        return content.find(id=self)['value']


class BlogScraper:

    TITLE_MGR = TitleMgr(LIST_TITLES)

    @classmethod
    def get_name_from_post(cls, post: Post, parsed: BeautifulSoup | None = None) -> str:
        ''' Dado un post del blog, devuelve el nombre con el que aparece en el Word'''

        name = post.title
        # Si el nombre que tiene en el word no es el normal, es que tiene un año
        with suppress(StopIteration):
            return cls.TITLE_MGR.exact_key(name, no_except=False)

        # Parseo el contenido
        if parsed is None:
            parsed = BeautifulSoup(post.content, 'lxml')

        # Tomo el nombre que está escrito en los datos ocultos
        name = BlogHiddenData.TITLE.get(parsed)
        with suppress(StopIteration):
            return cls.TITLE_MGR.exact_key(name, no_except=False)

        # El nombre que viene en el html no es correcto,
        # pruebo a componer un nuevo nombre con el título y el año
        year = BlogHiddenData.YEAR.get(parsed)
        name = f'{name} ({year})'

        with suppress(StopIteration):
            return cls.TITLE_MGR.exact_key(name, no_except=False)

        # Intento encontrar una reseña cuyo primer párrafo
        # sea idéntico al primer párrafo del texto
        with suppress(ValueError):
            return find_title_by_content(parsed)

        raise ValueError

    def __init__(self, post: Post):
        self.post = post
        self._parsed = BeautifulSoup(post.content, 'lxml')

    def get_post_link(self) -> str:
        return self.post.url

    def get_hidden_data(self, data: BlogHiddenData) -> str:
        return data.get(self._parsed)

    def get_title(self) -> str:
        return self.get_name_from_post(self.post)


def find_title_by_content(parsed_post: BeautifulSoup) -> str:

    # Variable de títulos posibles
    candidates_titles = BlogScraper.TITLE_MGR.list_titles()
    # Iteradores para todas las reseñas
    candidates_texts = {title: review_in_plain_text(title)
                        for title in candidates_titles}

    # Comparo párrafos hasta que sólo haya un título cuya reseña coincida
    for post_parr in parrs_in_plain_text(parsed_post):
        candidates_texts = filter_candidates(post_parr, candidates_texts)

        # Si no he encontrado coincidencia, no puedo sugerir ningún título
        if not candidates_texts:
            raise ValueError
        # Sólo hay una coincidencia, sugiero ese título
        elif len(candidates_texts) == 1:
            return next(iter(candidates_texts))

    # Se ha llegado al improbable caso en el que hay dos reseñas con los mismos párrafos
    raise ValueError


def filter_candidates(paragraph: str, candidates: dict[str, Iterator[str]]) -> dict[str, Iterator[str]]:
    # Títulos cuyo párrafo i-ésimo coincide con el párrafo introducido
    filtered_candidates = [title for title, iter_text in candidates.items()
                           if paragraph == next(iter_text, None)]

    # Devuelvo el diccionario con sólo los títulos que me sirven
    return {title: candidates[title] for title in filtered_candidates}


def review_in_plain_text(title: str) -> Iterator[str]:
    # Itero hasta el párrafo cuyo índice coincide con el necesario
    for i, current_title_parr in enumerate(WordReader.iter_review(title)):
        # Lo convierto a texto consecutivo
        parr_text = ''.join(run.text for run in current_title_parr.runs)
        # Retiro el título antes de los dos puntos
        if i == 0:
            parr_text = parr_text[len(title):]
            parr_text = parr_text.lstrip(": ")

        yield parr_text


def parrs_in_plain_text(parsed_post: BeautifulSoup) -> Iterator[str]:

    # Convierto el primer párrafo a texto plano
    for parr in iter_BeautifulSoup(parsed_post, 'p', class_=['regular-parr', 'quoted-parr']):
        # Obtengo solo el texto
        all_text: list[str] = parr.find_all(string=True)
        # Elimino la sangría del inicio del párrafo
        all_text[0] = all_text[0].lstrip()
        # Elimino el último salto de línea del final del párrafo
        all_text[-1] = all_text[-1].rstrip()
        text = ''.join(all_text)
        # Sustituyo los saltos de línea
        text = text.replace("\n", " ")

        yield text


def iter_BeautifulSoup(parsed_page: BeautifulSoup, /, *args, **kwargs) -> Iterator[BeautifulSoup]:
    found = parsed_page.find(*args, **kwargs)
    while found is not None:
        yield found
        found = found.find_next(*args, **kwargs)
