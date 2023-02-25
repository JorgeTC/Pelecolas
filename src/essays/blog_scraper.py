from enum import StrEnum

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

    first_parr = first_parr_in_plain_text(parsed_post)

    # Itero los títulos y me fijo en el párrafo
    for title in LIST_TITLES:
        current_title_parr = next(WordReader.iter_review(title))
        if first_parr == current_title_parr.text:
            return title

    return ""


def first_parr_in_plain_text(parsed_post: BeautifulSoup) -> str:

    # Convierto el primer párrafo a texto plano
    first_parr = parsed_post.find('p', {'class': 'regular-parr'})
    return first_parr.attrs[0]
