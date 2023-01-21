import enum
import urllib.parse

from bs4 import BeautifulSoup

from src.aux_title_str import split_title_year
from src.pelicula import Pelicula
from src.safe_url import safe_get_url


class SearchResult(enum.IntEnum):
    '''Determinar qué se ha encontrado al buscar la película en FA'''
    ENCONTRADA = enum.auto()
    VARIOS_RESULTADOS = enum.auto()
    NO_ENCONTRADA = enum.auto()
    ERROR = enum.auto()


# Mensajes para emitir por consola
SZ_ONLY_ONE_FILM = "Se ha encontrado una única película llamada {}.".format
SZ_ONLY_ONE_FILM_YEAR = "Se ha encontrado una única película llamada {} del año {}".format

# Link para buscar una película
URL_SEARCH = "https://www.filmaffinity.com/es/search.php?stype=title&stext={}".format


class Searcher:

    def __init__(self, to_search: str):
        # Separo en la cadena introducida el título y el año
        year, self.title = split_title_year(to_search)

        # Si ha encontrado un año, lo convierto a entero
        try:
            self.año = int(year)
        except ValueError:
            self.año = 0

        # Creo la url para buscar ese título
        self.search_url = get_search_url(self.title)

        # Creo una variable para cuando encuentre a película
        self.__coincidente: Pelicula = None

        # Guardo la página de búsqueda parseada.
        req = safe_get_url(self.search_url)
        self.parsed_page = BeautifulSoup(req.text, 'lxml')

        # Ya he hecho la búsqueda.
        # Quiero saber qué se ha conseguido, en qué caso estamos.
        # Antes de hacer esta distinción, necesito ver si FilmAffinity me ha redirigido.
        self.film_url = get_redirected_url(self.parsed_page)
        self.__estado = clarify_case(self.film_url)

    def __search_boxes(self) -> list[Pelicula]:

        # Sólo tengo un listado de películas encontradas cuando tenga muchos resultados.
        if self.__estado != SearchResult.VARIOS_RESULTADOS:
            return []

        # Caja donde están todos los resultados
        peliculas_encontradas: list[BeautifulSoup] = \
            self.parsed_page.find_all('div', {'class': 'se-it'})

        lista_peliculas = []
        curr_year = 0

        for p in peliculas_encontradas:
            # Leo el año...
            if len(p.get('class')) > 1:
                year = p.find('div', {'class': 'ye-w'})
                curr_year = int(year.contents[0])

            # ...si no encuentro el año, el año que ya tengo leído me sirve.

            # Leo el título y el enlace
            title_box = p.find('div', {'class': 'mc-title'})
            url: str = title_box.contents[0].attrs['href']
            title: str = title_box.contents[0].attrs['title']
            title = title.strip()

            # Lo añado a la lista
            film = Pelicula()
            film.titulo = title
            film.año = curr_year
            film.url_FA = url
            lista_peliculas.append(film)

        return lista_peliculas

    def encontrada(self) -> bool:
        return self.__estado == SearchResult.ENCONTRADA

    def resultados(self) -> bool:
        # Comprobar si hay esperanza de encontrar la ficha
        return self.__estado == SearchResult.ENCONTRADA or self.__estado == SearchResult.VARIOS_RESULTADOS

    def get_url(self) -> str:
        # Una vez hechas todas las consideraciones,
        # me devuelve la ficha de la película que ha encontrado.
        if self.__estado == SearchResult.ENCONTRADA:
            return self.film_url

        if self.__estado == SearchResult.VARIOS_RESULTADOS:
            lista_peliculas = self.__search_boxes()
            self.film_url = self.__elegir_url(lista_peliculas)
            return self.film_url

        # No he sido capaz de encontrar nada
        return ""

    def __elegir_url(self, lista: list[Pelicula]) -> str:
        # Tengo una lista de películas con sus años.
        # Miro cuál de ellas me sirve más.

        def is_coincident(candidate: Pelicula) -> bool:
            # Si el año no coincide, no es esta la película que busco
            if self.año and self.año != candidate.año:
                return False

            # Si el título coincide, devuelvo esa url.
            if self.title.lower() == candidate.titulo.lower():
                return True

            return False

        # Guardo todas las que sean coincidentes.
        # Espero que sólo sea una.
        coincidentes = [film for film in lista if is_coincident(film)]

        # Una vez hecha la búsqueda, miro cuántas películas me sirven.
        if len(coincidentes) == 1:
            self.__coincidente = coincidentes[0]
            return self.__coincidente.url_FA
        else:
            # Hay varios candidatos igual de válidos.
            # no puedo devolver nada con certeza.
            return ""

    def print_state(self):

        # Si no se ha encontrado nada, no hay nada que imprimir
        if not self.resultados():
            return

        # He encontrado la película
        if self.__estado == SearchResult.ENCONTRADA:
            print(SZ_ONLY_ONE_FILM(self.title))
            return

        # Tengo varias películas
        # if self.__estado == VARIOS_RESULTADOS:
        # Llamo al cálculo de self.film_url
        self.get_url()
        if self.film_url:
            print(SZ_ONLY_ONE_FILM_YEAR(self.title, self.__coincidente.año))


def clarify_case(film_url: str) -> SearchResult:

    # Ya me han redireccionado
    # Mirando la url puedo distinguir los tres casos.
    # Me quedo con la información inmediatamente posterior al idioma.
    stage = film_url[32:]

    # El mejor de los casos, he encontrado la película
    if stage.find('film') >= 0:
        return SearchResult.ENCONTRADA
    if stage.find('advsearch') >= 0:
        return SearchResult.NO_ENCONTRADA
    if stage.find('search') >= 0:
        return SearchResult.VARIOS_RESULTADOS

    return SearchResult.ERROR


def get_search_url(title) -> str:
    # Convierto los caracteres no alfanuméricpos en hexadecimal
    # No puedo convertir los espacios:
    # FilmAffinity convierte los espacios en +.
    title_for_url = urllib.parse.quote(title, safe=" ")

    # Cambio los espacios para poder tener una sola url
    title_for_url = title_for_url.replace(" ", "+")

    # Devuelvo la dirección de búsqueda
    return URL_SEARCH(title_for_url)


def get_redirected_url(parsed_page: BeautifulSoup) -> str:
    return parsed_page.find('meta', property='og:url')['content']


if __name__ == '__main__':
    # searc = Searcher("El milagro de P. Tinto")
    searc = Searcher("caza")
    searc.get_url()
