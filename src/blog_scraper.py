from bs4 import BeautifulSoup

from src.api_dataclasses import Post
from src.blog_csv_mgr import BlogCsvMgr
from src.list_title_mgr import TitleMgr
from src.poster import Poster
from src.read_blog import BlogHiddenData
from src.word_reader import WordReader


class BlogScraper:

    HEADER_CSV = ('Titulo', 'Link', 'Director', 'Año')
    TITLE_MGR = TitleMgr(WordReader().list_titles())

    @classmethod
    def get_name_from_post(cls, post: Post) -> str:
        name = post.title
        # Si el nombre que tiene en el word no es el normal, es que tiene un año
        if cls.TITLE_MGR.is_title_in_list(name):
            return cls.TITLE_MGR.exact_key_without_dlg(name)

        # Parseo el contenido
        parsed = BeautifulSoup(post.content, 'html.parser')

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

        return ""

    @classmethod
    def get_data_from_post(cls, post: Post) -> tuple[str]:
        link = post.url
        body = BeautifulSoup(post.content, 'html.parser')
        director = BlogHiddenData.DIRECTOR.get(body)
        año = BlogHiddenData.YEAR.get(body)
        name = cls.get_name_from_post(post)

        return name, link, director, año

    @classmethod
    def write_csv(cls):

        # Lista de reseñas desde que empezó el blog
        posted = Poster.get_all_active_posts()

        # Quiero extraer datos de cada reseña para escribir el csv
        extracted_data = (cls.get_data_from_post(post) for post in posted)

        BlogCsvMgr.write(cls.HEADER_CSV, extracted_data)


def main():
    BlogScraper.write_csv()


if __name__ == '__main__':
    main()
