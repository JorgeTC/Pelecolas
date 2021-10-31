import csv
from concurrent import futures
from datetime import date
from pathlib import Path

from bs4 import BeautifulSoup
from pandas import DateOffset

from .safe_url import safe_get_url


class BlogScraper():
    BLOG_SITE = 'https://pelecolas.blogspot.com'

    HEADER_CSV = ['Titulo', 'Link', 'Director']

    def __init__(self) -> None:
        # Guardo el mes actual
        self.__last_month = date.today()
        # Guardo el primer mes que tiene reseña
        self.__first_month = date(2019, 5, 1)

        # Creo el csv donde guardo los datos de las entradas
        # Obtengo la dirección del csv
        sz_curr_folder = Path(__file__).resolve().parent
        sz_csv_folder = sz_curr_folder / "Make_html"
        sz_csv_file = sz_csv_folder / "bog_data.csv"
        # Abro el archivo y se lo doy al objeto que escribe el csv
        self.__csv_file = open(sz_csv_file, 'w', encoding="utf-8", newline='')
        self.__csv_writer = csv.writer(self.__csv_file)
        # Escribo el header del csv
        self.__csv_writer.writerow(self.HEADER_CSV)

    def __del__(self):
        # Cuando se elimina la clase, cierro el archivo
        self.__csv_file.close()

    def get_month_dir(self, month: date):
        # Empiezo con la dirección del blog
        sz_dir = self.BLOG_SITE + "/"
        # Añado el año
        sz_dir = sz_dir + str(month.year) + "/"
        # Añado el mes
        sz_dir = sz_dir + '{:02d}'.format(month.month) + "/"

        return sz_dir

    def get_data_from_month(self, month: date):
        # Obtengo la dirección del mes inrtoducido
        sz_dir = self.get_month_dir(month)
        # Descargo la página
        text = safe_get_url(sz_dir)
        # Parseo la página
        parsed_page = BeautifulSoup(text.text, 'html.parser')
        # Obtengo una lista de todas las reseñas
        reseñas = parsed_page.find("div", {"class": "blog-posts hfeed"})
        reseñas = reseñas.find_all("div", {"class": "date-outer"})
        reseñas = [i.find('div', itemprop='blogPost') for i in reseñas]

        ans_data = []

        # Itero las reseñas para sacarles los datos
        for reseña in reseñas:

            # Trabajo el encabezado, quiero su nombre y su dirección
            header = reseña.find('h3', itemprop='name')
            name = header.contents[1].contents[0]
            link = header.contents[1].attrs['href']
            # Trabajo el cuerpo, quiero director
            body = reseña.find('div', itemprop='description articleBody')
            director = body.find('div').contents[1].contents[0]
            director = director[director.find(':') + 1:].strip()

            datos = [name, link, director]
            ans_data.append(datos)

        return ans_data

    def write_csv(self):
        # Hago la lista de los meses en los que quiero leer
        months = []
        curr_month = self.__first_month
        while curr_month <= self.__last_month:
            months.append(curr_month)
            curr_month = curr_month + DateOffset(months=1)

        # Creo un objeto para hacer la gestión de paralelización
        executor = futures.ThreadPoolExecutor(max_workers=20)
        extracted_data = list(executor.map(self.get_data_from_month, months))
        to_write = [i for month in extracted_data for i in month]
        # Escribo lo leído en el csv
        self.__csv_writer.writerows(to_write)


def main():
    innn = BlogScraper()
    innn.write_csv()


if __name__ == '__main__':
    main()
