from concurrent import futures
from datetime import date

from bs4 import BeautifulSoup
from pandas import DateOffset

from src.read_blog import ReadBlog
from src.blog_csv_mgr import BlogCsvMgr
from src.safe_url import safe_get_url

BLOG_MONTH = 'https://pelecolas.blogspot.com/{}/{:02d}/'.format


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

    def get_month_dir(self, month: date):
        # Dirección del blog, año y mes
        return BLOG_MONTH(month.year, month.month)

    def get_data_from_month(self, sz_dir: str):
        # Descargo la página
        text = safe_get_url(sz_dir)
        # Parseo la página
        parsed_page = BeautifulSoup(text.text, 'html.parser')
        # Obtengo una lista de todas las reseñas
        reseñas = parsed_page.find_all("div", {"class": "date-outer"})
        reseñas = [i.find('div', itemprop='blogPost') for i in reseñas]

        ans_data = []

        # Itero las reseñas para sacarles los datos
        for reseña in reseñas:

            # Trabajo el encabezado, quiero su nombre y su dirección
            header = reseña.find('h3', itemprop='name')
            name = header.contents[1].contents[0]
            link = header.contents[1].attrs['href']
            # Trabajo el cuerpo, quiero director y año
            body = reseña.find('div', itemprop='description articleBody')
            # Le paso el cuerpo parseado
            director, año = self.get_director_year_from_content(body)

            datos = [name, link, director, año]
            ans_data.append(datos)

        return ans_data

    def write_csv(self):
        # Escribo el header del csv
        self.__csv_writer = self.open_to_write()
        self.__csv_writer.writerow(self.HEADER_CSV)

        # Hago la lista de los meses en los que quiero leer
        months = []
        curr_month = self.__first_month
        while curr_month <= self.__last_month:
            months.append(curr_month)
            curr_month = curr_month + DateOffset(months=1)
        months_url = [self.get_month_dir(month) for month in months]

        # Creo un objeto para hacer la gestión de paralelización
        executor = futures.ThreadPoolExecutor(max_workers=20)
        extracted_data = list(executor.map(
            self.get_data_from_month, months_url))
        to_write = [i for month in extracted_data for i in month]
        # Escribo lo leído en el csv
        self.__csv_writer.writerows(to_write)

        self.exists_csv = True


def main():
    innn = BlogScraper()
    innn.write_csv()


if __name__ == '__main__':
    main()
