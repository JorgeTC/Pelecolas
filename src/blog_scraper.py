from concurrent import futures

from bs4 import BeautifulSoup

from src.read_blog import BlogHiddenData
from src.blog_csv_mgr import BlogCsvMgr
from src.poster import Poster


class BlogScraper(BlogCsvMgr):

    HEADER_CSV = ['Titulo', 'Link', 'Director', 'Año']

    def __init__(self) -> None:
        # Abro el archivo y se lo doy al objeto que escribe el csv
        self.csv_file = None
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
        # Creo un objeto para paralelizar el proceso
        with futures.ThreadPoolExecutor() as executor:
            extracted_data = list(executor.map(
                self.get_data_from_post, posted))

        self.__csv_writer.writerows(extracted_data)


def main():
    innn = BlogScraper()
    innn.write_csv()


if __name__ == '__main__':
    main()
