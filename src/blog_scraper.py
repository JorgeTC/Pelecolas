from bs4 import BeautifulSoup

from src.blog_csv_mgr import BlogCsvMgr
from src.poster import Poster
from src.read_blog import BlogHiddenData


class BlogScraper:

    HEADER_CSV = ('Titulo', 'Link', 'Director', 'Año')

    @classmethod
    def get_data_from_post(cls, post: dict) -> tuple[str]:
        name = post['title']
        link = post['url']
        body = BeautifulSoup(post['content'], 'html.parser')
        director = BlogHiddenData.DIRECTOR.get(body)
        año = BlogHiddenData.YEAR.get(body)

        return name, link, director, año

    @classmethod
    def write_csv(cls):

        # Lista de reseñas desde que empezó el blog
        posted = Poster.get_all_active_posts()

        # Quiero extraer datos de cada reseña para escribir el csv
        extracted_data = [cls.get_data_from_post(post) for post in posted]

        BlogCsvMgr.write(cls.HEADER_CSV, extracted_data)


def main():
    BlogScraper.write_csv()


if __name__ == '__main__':
    main()
