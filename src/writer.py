import enum
import re
from collections import namedtuple
from concurrent.futures import ThreadPoolExecutor
from math import ceil
from random import randint
from typing import Iterable

from bs4 import BeautifulSoup
from openpyxl.styles import Alignment, Font
from openpyxl.worksheet import worksheet

import src.url_FA as url_FA
from src.config import Config, Param, Section
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
    Prop_aprobados_FA = enum.auto()
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


FilmData = namedtuple("FilmData",
                      ("user_note",
                       "titulo",
                       "id",
                       "duracion",
                       "nota_FA",
                       "votantes_FA",
                       "desvest_FA",
                       "prop_aprobados"))


class Writer():

    USE_MULTI_THREAD = Config.get_bool(Section.READDATA, Param.PARALLELIZE)

    def __init__(self, worksheet: worksheet.Worksheet):

        # Barra de progreso
        self.bar = ProgressBar()

        # Hoja de excel
        self.ws = worksheet

    def read_sample(self) -> Iterable[FilmData]:
        # Creo un objeto para hacer la gestión de paralelización
        executor = ThreadPoolExecutor(max_workers=50)

        # Creo un generador aleatorio de ids de películas
        rnd = RandomFilmId()

        while rnd.size:
            # Lista de las películas válidas en la página actual.
            valid_film_list = (Pelicula.from_id(id)
                               for id in rnd.get_ids_lot(50))

            # Itero las películas en mi página actual
            if self.USE_MULTI_THREAD:
                iter_film_data = executor.map(
                    read_film_if_valid, valid_film_list)
            else:
                iter_film_data = (read_film_if_valid(film)
                                  for film in valid_film_list)

            for film_data in iter_film_data:
                if film_data.nota_FA:
                    yield film_data

    def write_sample(self, sample_size: int) -> None:
        # Creo una barra de progreso
        self.bar.reset_timer()

        # Número de películas leídas
        row = 0

        # Itero hasta que haya leído todas las películas
        for film_data in self.read_sample():
            self.__write_in_excel(row, film_data)
            row += 1

            # Actualizo la barra de progreso
            self.bar.update(row / sample_size)

            # Si ya tengo suficientes películas, salgo del bucle
            if row >= sample_size:
                break

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

    def __get_all_boxes(self, user_id: int, total_films: int) -> Iterable[Iterable[BeautifulSoup]]:
        n_pages = ceil(total_films / 20)
        url_pages = (url_FA.URL_USER_PAGE(user_id, i + 1)
                     for i in range(n_pages))

        executor = ThreadPoolExecutor()
        return executor.map(self.__list_boxes, url_pages)

    def __list_boxes(self, url: str) -> Iterable[BeautifulSoup]:
        resp = safe_get_url(url)
        # Guardo la página ya parseada
        soup_page = BeautifulSoup(resp.text, 'html.parser')
        # Leo todas las películas que haya en ella
        return soup_page.findAll("div", {"class": "user-ratings-movie"})

    def read_watched(self, id_user: int) -> Iterable[tuple[FilmData, float]]:

        # Votaciones en total
        total_films = self.get_total_films(id_user)

        # Creo un objeto para hacer la gestión de paralelización
        executor = ThreadPoolExecutor(max_workers=20)

        # Lista de todas las cajas de películas del usuario
        film_list = self.__get_all_boxes(id_user, total_films)
        # Contador de películas leídas
        film_index = 0

        # Itero hasta que haya leído todas las películas
        for page_boxes in film_list:
            # Lista de las películas válidas en la página actual.
            valid_film_list = (init_film_from_movie_box(box)
                               for box in page_boxes)
            valid_film_list = (film for film in valid_film_list
                               if film.valid())

            # Itero las películas en mi página actual
            if self.USE_MULTI_THREAD:
                iter_film_data = executor.map(read_film, valid_film_list)
            else:
                iter_film_data = (read_film(film) for film in valid_film_list)

            read_in_page = 0
            for film_data in iter_film_data:
                read_in_page += 1
                yield film_data, (film_index + read_in_page)/total_films

            # Avanzo a la siguiente página de películas vistas por el usuario
            film_index = min(film_index + 20, total_films)

    def write_watched(self, id_user: int):

        # Creo una barra de progreso
        self.bar.reset_timer()

        # Inicializo la fila actual en la que estoy escribiendo
        index = 0
        for film_data, progress in self.read_watched(id_user):
            self.__write_in_excel(index, film_data)
            index += 1
            self.bar.update(progress)

        self.bar.update(1)

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
                              film.titulo, id=film.id)

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
            self.__set_cell_value(line, ExcelColumns.Prop_aprobados_FA,
                                  film.prop_aprobados)

    def __set_cell_value(self, line: int, col: ExcelColumns, value, *, id=0):

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
        # Proporción de aprobados
        elif (col == ExcelColumns.Prop_aprobados_FA):
            cell.number_format = '0.00%'
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


def has_valid_id(film: Pelicula) -> bool:

    # Parseo la página.
    film.get_parsed_page()
    # compruebo si la página obtenida existe
    if not film.exists():
        return False

    # Obtengo el título de la película...
    try:
        film.get_title()
    except:
        return False
    # ...para comprobar si es válido
    if not film.valid():
        return False

    # Compruebo por último que tenga nota media
    film.get_nota_FA()
    if not film.nota_FA:
        return False

    # Si el id es válido, el título es válido y tiene nota en FA, es un id válido para mi estadística
    return True


def read_film(film: Pelicula) -> FilmData:
    # Hacemos la parte más lenta, que necesita parsear la página.
    film.get_nota_FA()
    film.get_votantes_FA()
    film.get_duracion()
    film.get_desvest()
    film.get_prop_aprobados()

    # Extraemos los datos que usaremos para que el objeto sea más pequeño
    return FilmData(film.user_note,
                    film.titulo,
                    film.id,
                    film.duracion,
                    film.nota_FA,
                    film.votantes_FA,
                    film.desvest_FA,
                    film.prop_aprobados)


def read_film_if_valid(film: Pelicula) -> FilmData:

    # Si la película no es válida devuelvo una tupla vacía
    if not has_valid_id(film):
        return FilmData(*((0,)*len(FilmData._fields)))

    # Es válida, devuelvo la tupla habitual
    try:
        return read_film(film)
    except:
        return FilmData(*((0,)*len(FilmData._fields)))


class RandomFilmId:
    def __init__(self) -> None:
        self.ids = list(range(100_000, 1_000_000))
        self.size = len(self.ids)

    def get_id(self) -> int:

        if self.size == 0:
            return 0

        self.size -= 1
        rand_index = randint(0, self.size)
        self.ids[self.size], self.ids[rand_index] = self.ids[rand_index], self.ids[self.size]

        return self.ids.pop()

    def get_ids_lot(self, lot_size: int) -> Iterable[int]:
        lot_size = min(lot_size, self.size)
        return (self.get_id() for _ in range(lot_size))
        
        
class FromFilmBox:
    '''Funciones para extraer datos de la caja de la película'''
    @staticmethod
    def get_title(film_box: BeautifulSoup) -> str:
        return film_box.contents[1].contents[1].contents[3].contents[1].contents[0].contents[0]

    @staticmethod
    def get_user_note(film_box: BeautifulSoup) -> int:
        return int(film_box.contents[3].contents[1].contents[1].contents[0])

    @staticmethod
    def get_id(film_box: BeautifulSoup) -> int:
        return int(film_box.contents[1].contents[1].attrs['data-movie-id'])

    @staticmethod
    def get_year(film_box: BeautifulSoup) -> int:
        str_year = str(
            film_box.contents[1].contents[1].contents[3].contents[1].contents[1])
        return int(re.search(r"(\d{4})", str_year).group(1))


def init_film_from_movie_box(movie_box: BeautifulSoup) -> Pelicula:
    instance = Pelicula()

    # Guardo los valores que conozco por la información introducida
    instance.titulo = FromFilmBox.get_title(movie_box)
    instance.user_note = FromFilmBox.get_user_note(movie_box)
    instance.id = FromFilmBox.get_id(movie_box)
    instance.url_FA = url_FA.URL_FILM_ID(instance.id)

    # Devuelvo la instancia
    return instance
