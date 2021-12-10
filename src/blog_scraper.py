from concurrent import futures
from datetime import date

from bs4 import BeautifulSoup

from src.read_blog import ReadBlog
from src.blog_csv_mgr import BlogCsvMgr
from src.poster import POSTER


class BlogScraper(BlogCsvMgr, ReadBlog):

    HEADER_CSV = ['Titulo', 'Link', 'Director', 'Año']

    def __init__(self) -> None:
        # Guardo el mes actual
        self.__last_month = date.today()
        # Guardo el primer mes que tiene reseña
        self.__first_month = date(2019, 5, 1)

        # Abro el archivo y se lo doy al objeto que escribe el csv
        self.csv_file = None
        self.__csv_writer = None

    def __del__(self):
        # Cuando se elimina la clase, cierro el archivo
        if self.csv_file:
            self.csv_file.close()

    def get_data_from_post(self, post):
        name = post['title']
        link = post['url']
        body = BeautifulSoup(post['content'], 'html.parser')
        director, año = self.get_director_year_from_content(body)

        return [name, link, director, año]

    def write_csv(self):
        # Escribo el header del csv
        self.__csv_writer = self.open_to_write()
        self.__csv_writer.writerow(self.HEADER_CSV)

        # Lista de reseñas desde que empezó el blog
        posted = POSTER.get_published_from_date(self.__first_month)

        executor = futures.ThreadPoolExecutor()
        extracted_data = list(executor.map(self.get_data_from_post, posted))

        self.__csv_writer.writerows(extracted_data)


def main():
    innn = BlogScraper()
    innn.write_csv()


if __name__ == '__main__':
    main()