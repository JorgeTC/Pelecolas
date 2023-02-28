from enum import StrEnum
from typing import Generator

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
    def get_name_from_post(cls, post: Post, parsed: BeautifulSoup = None) -> str:
        ''' Dado un post del blog, devuelve el nombre con el que aparece en el Word'''

        name = post.title
        # Si el nombre que tiene en el word no es el normal, es que tiene un año
        if cls.TITLE_MGR.is_title_in_list(name):
            return cls.TITLE_MGR.exact_key_without_dlg(name)

        # Parseo el contenido
        if parsed is None:
            parsed = BeautifulSoup(post.content, 'lxml')

        # Tomo el nombre que está escrito en los datos ocultos
        name = BlogHiddenData.TITLE.get(parsed)
        if cls.TITLE_MGR.is_title_in_list(name):
            return cls.TITLE_MGR.exact_key_without_dlg(name)

        # El nombre que viene en el html no es correcto,
        # pruebo a componer un nuevo nombre con el título y el año
        year = BlogHiddenData.YEAR.get(parsed)
        name = f'{name} ({year})'

        if cls.TITLE_MGR.is_title_in_list(name):
            return cls.TITLE_MGR.exact_key_without_dlg(name)

        # Intento encontrar una reseña cuyo primer párrafo
        # sea idéntico al primer párrafo del texto
        if name := find_title_by_content(parsed):
            return name

        return ""

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
    candidates_titles = BlogScraper.TITLE_MGR.TITLES

    # Comparo párrafos hasta que sólo haya un título cuya reseña coincida
    for i, post_parr in enumerate(parrs_in_plain_text(parsed_post)):
        # Candidatos después de haber comparado el i-ésimo párrafo
        filtered_candidates = []

        # Itero todos los posibles títulos
        for title in candidates_titles:
            word_parr_text = review_in_plain_text(title, i)
            # Coinciden, por tanto puede ser el título que busco
            if post_parr == word_parr_text:
                filtered_candidates.append(title)

        # Si no he encontrado coincidencia, no puedo sugerir ningún título
        if not filtered_candidates:
            return ""
        # Sólo hay una coincidencia, sugiero ese título
        elif len(filtered_candidates) == 1:
            return filtered_candidates[0]

        # Me quedo con los candidatos
        candidates_titles = filtered_candidates

    # Se ha llegado al improbable caso en el que hay dos reseñas con los mismos párrafos
    return ""


def review_in_plain_text(title: str, index_parr: int) -> str:
    # Itero hasta el párrafo cuyo índice coincide con el necesario
    for i, current_title_parr in enumerate(WordReader.iter_review(title)):
        if i < index_parr:
            continue

        # Lo convierto a texto consecutivo
        parr_text = ''.join(run.text for run in current_title_parr.runs)
        # Retiro el título antes de los dos puntos
        if i == 0:
            parr_text = parr_text[len(title):]
            parr_text = parr_text.lstrip(": ")

        return parr_text

    # He introducido un índice demasiado grande
    return ""


def parrs_in_plain_text(parsed_post: BeautifulSoup) -> Generator[str, None, None]:

    args_find_parr = ['p',
                      {'class': ['regular-parr', 'quoted-parr']}]

    # Convierto el primer párrafo a texto plano
    parr = parsed_post.find(args_find_parr)

    while parr is not None:
        # Obtengo solo el texto
        all_text: list[str] = parr.findAll(string=True)
        # Elimino la sangría del inicio del párrafo
        all_text[0] = all_text[0].lstrip()
        # Elimino el último salto de línea del final del párrafo
        all_text[-1] = all_text[-1].rstrip()
        text = ''.join(all_text)
        # Sustituyo los saltos de línea
        text = text.replace("\n", " ")

        yield text
        parr = parr.find_next(args_find_parr)
