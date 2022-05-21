import enum
from collections import namedtuple
from concurrent.futures import ThreadPoolExecutor
from math import ceil
from random import sample

from bs4 import BeautifulSoup
from openpyxl.styles import Alignment, Font
from openpyxl.worksheet import worksheet

import src.url_FA as url_FA
from src.pelicula import Pelicula
from src.progress_bar import ProgressBar
from src.safe_url import safe_get_url


class ExcelColumns(int, enum.Enum):
    Id = enum.auto()
    Mia = enum.auto()
    FA = enum.auto()
    Duracion = enum.auto()
    Visionados = enum.auto()
    Varianza_FA = enum.auto()
    FA_redondeo = enum.auto()
    Diferencia = enum.auto()
    Diferencia_abs = enum.auto()
    Me_ha_gustado = enum.auto()
    Mia_ruido = enum.auto()
    FA_ruido = enum.auto()
    Mia_rees = enum.auto()
    FA_rees = enum.auto()

    def __str__(self) -> str:
        return f"Tabla1[{self.name}]"


FilmData = namedtuple(
    "FilmData", "user_note titulo id duracion nota_FA votantes_FA desvest_FA")


class Writer():

    def __init__(self, worksheet: worksheet.Worksheet):

        # Barra de progreso
        self.bar = ProgressBar()

        # Hoja de excel
        self.ws = worksheet

    def read_sample(self, sample_size: int) -> None:
        # Creo un objeto para hacer la gestión de paralelización
        executor = ThreadPoolExecutor(max_workers=50)
        # Creo una lista de listas donde se guardarán los datos de las películas
        films_data: list[FilmData] = []

        # Creo un generador aleatorio de ids de películas
        ids = range(100_000, 1_000_000)
        ids = sample(ids, len(ids))

        # Creo una barra de progreso
        self.bar.reset_timer()

        # Itero hasta que haya leído todas las películas
        while len(films_data) < sample_size:
            # Lista de las películas válidas en la página actual.
            valid_film_list = [Pelicula.from_id(id)
                               for id in (ids.pop() for _ in range(50))]
            valid_film_list = [film for film in valid_film_list
                               if film.valid()]

            # Itero las películas en mi página actual
            curr_sample = list(executor.map(self.__read_film, valid_film_list))
            films_data += [film for film in curr_sample if film.nota_FA]

            # Avanzo a la siguiente página de películas vistas por el usuario
            self.bar.update(len(films_data)/sample_size)

        # Escribo en el Excel
        self.__dump_to_excel(films_data)

    def get_total_films(self, id_user: int) -> int:

        url = url_FA.URL_USER_PAGE(id_user, 1)
        resp = safe_get_url(url)
        # Guardo la página ya parseada
        soup_page = BeautifulSoup(resp.text, 'html.parser')

        # me espero que haya un único "value-box active-tab"
        mydivs = soup_page.find("a", {"class": "value-box active-tab"})
        stringNumber = str(mydivs.contents[3].contents[1])
        # Elimino el punto de los millares
        stringNumber = stringNumber.replace('.', '')
        return int(stringNumber)

    def __get_all_boxes(self, user_id: int, total_films: int) -> list[list[BeautifulSoup]]:
        n_pages = ceil(total_films / 20)
        url_pages = [url_FA.URL_USER_PAGE(user_id, i + 1)
                     for i in range(n_pages)]

        executor = ThreadPoolExecutor()
        return list(executor.map(self.__list_boxes, url_pages))

    def __list_boxes(self, url: str) -> list[BeautifulSoup]:
        resp = safe_get_url(url)
        # Guardo la página ya parseada
        soup_page = BeautifulSoup(resp.text, 'html.parser')
        # Leo todas las películas que haya en ella
        return list(soup_page.findAll("div", {"class": "user-ratings-movie"}))

    def read_watched(self, id_user: int):

        # Votaciones en total
        total_films = self.get_total_films(id_user)

        # Creo un objeto para hacer la gestión de paralelización
        executor = ThreadPoolExecutor(max_workers=20)
        # Creo una lista de listas donde se guardarán los datos de las películas
        films_data: list[FilmData] = []

        # Inicializo un contador de las películas que ya he leído
        film_index = 0
        # Lista de todas las cajas de películas del usuario
        film_list = self.__get_all_boxes(id_user, total_films)

        # Creo una barra de progreso
        self.bar.reset_timer()

        # Itero hasta que haya leído todas las películas
        while film_list:
            # Lista de las películas válidas en la página actual.
            valid_film_list = [Pelicula.from_movie_box(box)
                               for box in film_list.pop()]
            valid_film_list = [film for film in valid_film_list
                               if film.valid()]

            # Itero las películas en mi página actual
            films_data += list(executor.map(self.__read_film, valid_film_list))

            # Avanzo a la siguiente página de películas vistas por el usuario
            film_index = min(film_index + 20, total_films)

            self.bar.update(film_index/total_films)

        # Escribo en el Excel
        self.__dump_to_excel(films_data)

    def __read_film(self, film: Pelicula) -> FilmData:
        # Hacemos la parte más lenta, que necesita parsear la página.
        film.get_time_and_FA()

        # Extraemos los datos que usaremos para que el objeto sea más pequeño
        return FilmData(film.user_note,
                        film.titulo,
                        film.id,
                        film.duracion,
                        film.nota_FA,
                        film.votantes_FA,
                        film.desvest_FA)

    def __dump_to_excel(self, films_data: list[FilmData]) -> None:
        self.bar.reset_timer()
        total_rows = len(films_data)
        index = 0
        while films_data:
            self.__write_in_excel(index, films_data.pop())
            index += 1
            self.bar.update(index / total_rows)

    def __write_in_excel(self, line: int, film: FilmData):

        # La enumeración empezará en 0,
        # pero sólo escribimos datos a partir de la segunda linea.
        line = line + 2

        # La votación del usuario la leo desde fuera
        # no puedo leer la nota del usuario dentro de la ficha
        self.__set_cell_value(line, ExcelColumns.Mia,
                              film.user_note)
        self.__set_cell_value(line, ExcelColumns.Mia_ruido,
                              f"={ExcelColumns.Mia}+RAND()-0.5")
        self.__set_cell_value(line, ExcelColumns.Mia_rees,
                              f"=({ExcelColumns.Mia}-1)*10/9")
        # En la primera columna guardo la id para poder reconocerla
        self.__set_cell_value(line, ExcelColumns.Id,
                              film.titulo, film.id)

        if (film.duracion != 0):
            # dejo la casilla en blanco si no logra leer ninguna duración de FA
            self.__set_cell_value(line, ExcelColumns.Duracion,
                                  film.duracion)

        if (film.nota_FA != 0):
            # dejo la casilla en blanco si no logra leer ninguna nota de FA
            self.__set_cell_value(line, ExcelColumns.FA,
                                  film.nota_FA)
            self.__set_cell_value(line, ExcelColumns.FA_redondeo,
                                  f"=ROUND({ExcelColumns.FA}*2, 0)/2")
            self.__set_cell_value(line, ExcelColumns.Diferencia,
                                  f"={ExcelColumns.Mia}-{ExcelColumns.FA}")
            self.__set_cell_value(line, ExcelColumns.Diferencia_abs,
                                  f"=ABS({ExcelColumns.Diferencia})")
            self.__set_cell_value(line, ExcelColumns.Me_ha_gustado,
                                  f"=IF({ExcelColumns.Diferencia}>0,1,0.1)")
            self.__set_cell_value(line, ExcelColumns.FA_rees,
                                  f"=({ExcelColumns.FA}-1)*10/9")
            self.__set_cell_value(line, ExcelColumns.FA_ruido,
                                  f"={ExcelColumns.FA}+(RAND()-0.5)/10")

        if (film.votantes_FA != 0):
            # dejo la casilla en blanco si no logra leer ninguna votantes
            self.__set_cell_value(line, ExcelColumns.Visionados,
                                  film.votantes_FA)

        if (film.desvest_FA != 0):
            self.__set_cell_value(line, ExcelColumns.Varianza_FA,
                                  film.desvest_FA)

    def __set_cell_value(self, line: int, col: ExcelColumns, value, id=0):

        # Obtengo un objeto celda
        cell = self.ws.cell(row=line, column=col)
        # Le asigno el valor
        cell.value = value

        # Configuramos el estilo de la celda atendiendo a su columna
        # visionados. Ponemos punto de millar
        if (col == ExcelColumns.Visionados):
            cell.number_format = '#,##0'
        # booleano mayor que
        elif (col == ExcelColumns.Me_ha_gustado):
            cell.number_format = '0'
            cell.font = Font(name='SimSun', bold=True)
            cell.alignment = Alignment(horizontal='center', vertical='center')
        # Nota del usuario más el ruido
        elif (col == ExcelColumns.Mia_ruido):
            cell.number_format = '0.0'
        # Nota de FA más el ruido
        elif (col == ExcelColumns.FA or
              col == ExcelColumns.FA_ruido):
            cell.number_format = '0.00'
        # Varianza de los votos en FA
        elif (col == ExcelColumns.Varianza_FA):
            cell.number_format = '0.00'
        # reescala
        elif (col == ExcelColumns.Mia_rees or
              col == ExcelColumns.FA_rees or
              col == ExcelColumns.Diferencia or
              col == ExcelColumns.Diferencia_abs):
            cell.number_format = '0.00'
        # Nombre de la película con un hipervínculo
        elif (col == ExcelColumns.Id):
            # Añado un hipervínculo a su página
            cell.style = 'Hyperlink'
            cell.hyperlink = url_FA.URL_FILM_ID(id)
            # Fuerzo el formato como texto
            cell.number_format = '@'
