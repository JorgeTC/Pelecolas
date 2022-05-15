from typing import TextIO

from bs4 import BeautifulSoup

from src.read_blog import BlogHiddenData
from src.blog_csv_mgr import BlogCsvMgr
from src.poster import Poster


class BlogScraper(BlogCsvMgr):

    HEADER_CSV = ['Titulo', 'Link', 'Director', 'Año']

    def __init__(self) -> None:
        # Abro el archivo y se lo doy al objeto que escribe el csv
        self.csv_file: TextIO = None
        self.__csv_writer = None

    def __del__(self):
        # Cuando se elimina la clase, cierro el archivo
        if self.csv_file:
            self.csv_file.close()

    def get_data_from_post(self, post: dict) -> tuple[str]:
        name = post['title']
        link = post['url']
        body = BeautifulSoup(post['content'], 'html.parser')
        director = BlogHiddenData.DIRECTOR.get(body)
        año = BlogHiddenData.YEAR.get(body)

        return name, link, director, año

    def write_csv(self):
        # Escribo el header del csv
        self.__csv_writer = self.open_to_write()
        self.__csv_writer.writerow(self.HEADER_CSV)

        # Lista de reseñas desde que empezó el blog
        posted = Poster.get_all_active_posts()

        # Quiero extraer datos de cada reseña para escribir el csv
        extracted_data = [self.get_data_from_post(post) for post in posted]

        self.__csv_writer.writerows(extracted_data)
        # Guardo el archivo
        self.csv_file.close()


def main():
    innn = BlogScraper()
    innn.write_csv()


if __name__ == '__main__':
    main()
