from concurrent.futures import Future
from http import HTTPStatus
from itertools import count
from queue import Queue
from threading import Thread
from typing import Iterable

from bs4 import BeautifulSoup

from src.pelicula import Pelicula
from src.safe_url import safe_get_url

from ..film_box import FilmBox
from ..utils import is_valid


class ReadWatched:
    def __init__(self, user_id: int) -> None:
        self.user_id = user_id
        self.results: Queue[Pelicula | None] = Queue()
        self.total_films = get_total_films(self.user_id)
        self.box_list = get_all_boxes(self.user_id, self.total_films)
        self.index = -1

        Thread(target=self.read_watched).start()

    @property
    def proportion(self) -> float:
        return (self.index + 1) / self.total_films

    @property
    def valid_film_list(self) -> Iterable[Pelicula | None]:
        # Lista de las películas válidas en la página actual.
        films_list = (self.init_film(box) for box in self.box_list)
        valid_film_list = (film if is_valid(film) else None
                           for film in films_list)

        return valid_film_list

    def read_watched(self) -> None:
        # Iteración convencional de valid_film_list
        for self.index, film in enumerate(self.valid_film_list):
            # Si la película no es None, la leo
            if film is not None:
                self.results.put(self.read_film(film))

        # Añado un None para saber cuándo he acabado la iteración
        self.results.put(None)

    def iter(self) -> Iterable[Pelicula]:
        while (film := self.results.get()):
            yield film

    def add_to_queue(self, result: Future):
        self.index += 1
        if (film := result.result()):
            self.results.put(film)

    @staticmethod
    def init_film(box: FilmBox) -> Pelicula:
        raise NotImplementedError

    @staticmethod
    def read_film(film: Pelicula) -> Pelicula:
        return film


# Link para acceder a cada página de un usuario
URL_USER_PAGE = 'https://www.filmaffinity.com/es/userratings.php?user_id={}&p={}&orderby=4&chv=list'.format


def get_total_films(id_user: int) -> int:

    url = URL_USER_PAGE(id_user, 1)
    resp = safe_get_url(url)
    # Guardo la página ya parseada
    soup_page = BeautifulSoup(resp.text, 'lxml')

    # me espero que haya un único "active-filter"
    active_filter = soup_page.find("div", class_="active-filter")
    films_count = active_filter.find("span", class_="count")
    string_number = str(films_count.text).strip()
    # Elimino el punto de los millares
    string_number = string_number.replace('.', '')
    return int(string_number)


def count_total_pages(total_films: int) -> int:
    # Ceil division by the number of elements in each page (50 per page)
    FILMS_PER_PAGE = 50
    return (total_films + FILMS_PER_PAGE - 1) // FILMS_PER_PAGE


def yield_all_boxes(user_id: int, total_films: int) -> Iterable[FilmBox]:
    url_pages = (URL_USER_PAGE(user_id, i + 1) for i in range(0, count_total_pages(total_films)))

    # Itero todas las páginas del actual usuario
    for url_page in url_pages:

        resp = safe_get_url(url_page)
        # Si la página no se encuentra, es que ya he leído todas
        if resp.status_code == HTTPStatus.NOT_FOUND:
            break

        # Guardo la página ya parseada
        soup_page = BeautifulSoup(resp.text, 'lxml')
        # Itero la página actual
        yield from list_boxes(soup_page)


def get_all_boxes(user_id: int, total_films: int) -> Iterable[FilmBox]:
    # Devuelve todas las cajas de las películas de un usuario.
    # Al terminar lanza un error si no se encuentran tantas películas como se esperaban

    for yielded_films, box in enumerate(yield_all_boxes(user_id, total_films), start=1):
        yield box

    if yielded_films != total_films:
        raise ValueError(f"Se esperaban {total_films} películas "
                         f"y se han encontrado {yielded_films}")


def list_boxes(soup_page: BeautifulSoup) -> Iterable[FilmBox]:
    # Leo todas las películas que haya en la página, ya parseada
    return (FilmBox(parsed_box) for parsed_box in
            soup_page.findAll("div", class_="row mb-4"))
