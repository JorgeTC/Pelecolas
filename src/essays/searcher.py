import enum
import urllib.parse
from itertools import islice
from typing import Iterator

from bs4 import BeautifulSoup

from src.pelicula import FilmInfoBox, Pelicula
from src.safe_url import safe_get_url

from .aux_title_str import split_title_year


class SearchResult(enum.IntEnum):
    '''Determinar qué se ha encontrado al buscar la película en FA'''
    FOUND = enum.auto()
    SEVERAL_RESULTS = enum.auto()
    NOT_FOUND = enum.auto()


# Mensajes para emitir por consola
SZ_ONLY_ONE_FILM = "Se ha encontrado una única película llamada {}.".format
SZ_ONLY_ONE_FILM_YEAR = "Se ha encontrado una única película llamada {} del año {}".format

# Link para buscar una película con coincidencia exacta
URL_SEARCH_EM = "https://www.filmaffinity.com/es/search.php?stype=title&stext={}&em=1".format
# Link para buscar una película con el método clásico
URL_SEARCH = "https://www.filmaffinity.com/es/search.php?stype=title&stext={}".format


def parse_title_and_year(to_search: str) -> tuple[str, int]:
    # Separo en la cadena introducida el título y el año
    year_str, title = split_title_year(to_search)

    # Si ha encontrado un año, lo convierto a entero
    try:
        year = int(year_str)
    except ValueError:
        year = 0

    return title, year


class Searcher:

    def __init__(self, to_search: str):
        # Datos de la película a buscar
        self.title, self.año = parse_title_and_year(to_search)

        # Realizo la búsqueda inicial
        self._do_search(self.title)

        # Si hay varios resultados, intento búsqueda exacta
        if self.__estado == SearchResult.SEVERAL_RESULTS:
            self._do_search(self.title, exact_match=True)

    def _do_search(self, title: str, exact_match: bool = False):
        """Realiza la búsqueda y actualiza los atributos relevantes."""
        # Creo la url de búsqueda
        self.search_url = get_search_url(title, exact_match=exact_match)
        # Guardo la página de búsqueda parseada
        req = safe_get_url(self.search_url)
        self.parsed_page = BeautifulSoup(req.text, 'lxml')

        # Ya he hecho la búsqueda.
        # Quiero saber qué se ha conseguido, en qué caso estamos.
        # Obtengo la dirección después de haber sido redirigido
        self.film_url = req.url
        self.__estado = clarify_case(self.film_url)

    def has_results(self) -> bool:
        # Comprobar si hay esperanza de encontrar la ficha
        return self.__estado in {SearchResult.FOUND, SearchResult.SEVERAL_RESULTS}

    def get_url(self) -> str:
        if self.__estado == SearchResult.SEVERAL_RESULTS:
            if coincident := self.get_coincident():
                self.film_url = coincident.url_FA
            return self.film_url if coincident is not None else ""

        if self.__estado == SearchResult.FOUND:
            # Si tenemos año, comprobamos que la película encontrada sea del año correcto
            if self.año:
                film = Pelicula.from_fa_url(self.film_url)
                film.get_año()
                if film.año != self.año:
                    return ""
            return self.film_url

        # No he sido capaz de encontrar nada
        return ""

    def get_coincident(self) -> Pelicula | None:
        films_list = search_boxes(self.parsed_page)
        return choose_film_result(self.title, self.año, films_list)

    def print_state(self):

        # Si no se ha encontrado nada, no hay nada que imprimir
        if self.__estado == SearchResult.NOT_FOUND:
            return

        # He encontrado la película
        if self.__estado == SearchResult.FOUND:
            print(SZ_ONLY_ONE_FILM(self.title))
            return

        # Tengo varias películas
        if self.__estado == SearchResult.SEVERAL_RESULTS:
            # Llamo al cálculo de self.film_url
            if coincident := self.get_coincident():
                print(SZ_ONLY_ONE_FILM_YEAR(self.title, coincident.año))


def clarify_case(film_url: str) -> SearchResult:

    # Ya me han redireccionado
    # Mirando la url puedo distinguir los tres casos.
    # Me quedo con la información inmediatamente posterior al idioma.
    stage = film_url[32:]

    # El mejor de los casos, he encontrado la película
    if 'film' in stage:
        return SearchResult.FOUND
    if 'advsearch' in stage:
        return SearchResult.NOT_FOUND
    if 'search' in stage:
        return SearchResult.SEVERAL_RESULTS

    raise ValueError


def choose_film_result(target_title: str, target_year: int, film_results: Iterator[Pelicula]) -> Pelicula | None:
    # Tengo una lista de películas con sus años, miro cuál de ellas me sirve más

    # Guardo todas las que sean coincidentes, me espero que sólo sea una
    coincidents = (film for film in film_results
                   if is_coincident(film, target_title, target_year))
    coincidents = list(islice(coincidents, 2))

    # Tomo la única coincidencia
    if len(coincidents) == 1:
        return coincidents[0]
    else:
        # Hay varias películas igual de válidas, no devuelvo nada
        return None


def get_search_url(title: str, exact_match=False) -> str:
    # Convierto los caracteres no alfanuméricos en hexadecimal
    # No puedo convertir los espacios:
    # FilmAffinity convierte los espacios en +.
    title_for_url = urllib.parse.quote(title, safe=" ")

    # Cambio los espacios para poder tener una sola url
    title_for_url = title_for_url.replace(" ", "+")

    # Devuelvo la dirección de búsqueda
    if exact_match:
        return URL_SEARCH_EM(title_for_url)
    else:
        return URL_SEARCH(title_for_url)


def get_redirected_url(parsed_page: BeautifulSoup) -> str:
    return parsed_page.find('meta', property='og:url')['content']


def search_boxes(parsed_page: BeautifulSoup) -> Iterator[Pelicula]:
    # Itero las cajas de resultados
    for found_box in iter_BeautifulSoup(parsed_page, 'div', class_='item-search'):
        # Obtengo la sección que contiene la información sobre la película
        info_container = found_box.find('div', class_='mc-info-container')
        # Instancio el objeto que me devuelve los datos de esa caja
        film_info = FilmInfoBox(info_container)

        # Devuelvo un objeto Pelicula con la información que tengo
        film = Pelicula()
        film.titulo = film_info.get_title()
        film.url_FA = film_info.get_FA_url()
        film.año = film_info.get_year()
        yield film


def is_coincident(candidate: Pelicula, target_title: str, target_year: int) -> bool:
    # Si el año no coincide, no es esta la película que busco
    if target_year and target_year != candidate.año:
        return False

    # Si el título coincide, esta es la película que busco
    return target_title.lower() == candidate.titulo.lower()


def iter_BeautifulSoup(parsed_page: BeautifulSoup, /, *args, **kwargs) -> Iterator[BeautifulSoup]:
    found = parsed_page.find(*args, **kwargs)
    while found is not None:
        yield found
        found = found.find_next(*args, **kwargs)
