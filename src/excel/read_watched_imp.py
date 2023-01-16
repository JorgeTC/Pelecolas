from concurrent.futures import Future, ThreadPoolExecutor
from math import ceil
from queue import Queue
from threading import Thread
from typing import Iterable

from bs4 import BeautifulSoup

import src.url_FA as url_FA
from src.config import Config, Param, Section
from src.excel.film_box import FilmBox
from src.excel.utils import is_valid, read_film
from src.pelicula import Pelicula
from src.safe_url import safe_get_url


class ReadWatched:
    def __init__(self, user_id: int) -> None:
        self.user_id = user_id
        self.results: Queue[Pelicula] = Queue()
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
                self.results.put(read_film(film))

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


class ReadDataWatched(ReadWatched):
    def __init__(self, user_id: int) -> None:
        ReadWatched.__init__(self, user_id)

    def read_watched(self, *,
                     use_multithread=Config.get_bool(Section.READDATA, Param.PARALLELIZE)):
        if use_multithread:
            self.read_watched_parallel()
        else:
            ReadWatched.read_watched(self)

    def read_watched_parallel(self) -> None:
        exe = ThreadPoolExecutor(thread_name_prefix="ReadFilm")
        # Incluso aunque no tenga que leer la película la añado al Executor.
        # De lo contrario no se incrementaría la barra de progreso
        futures = (exe.submit(read_film, film) if film
                   else exe.submit(lambda *_: None, film)
                   for film in self.valid_film_list)
        for future in futures:
            future.add_done_callback(self.add_to_queue)
        exe.shutdown(wait=True)
        self.results.put(None)

    @staticmethod
    def init_film(movie_box: FilmBox) -> Pelicula:
        instance = Pelicula()

        # Guardo los valores que conozco por la información introducida
        instance.titulo = movie_box.get_title()
        instance.user_note = movie_box.get_user_note()
        instance.id = movie_box.get_id()
        instance.url_FA = url_FA.URL_FILM_ID(instance.id)

        # Devuelvo la instancia
        return instance


class ReadDirectorsWatched(ReadWatched):
    def __init__(self, user_id: int) -> None:
        ReadWatched.__init__(self, user_id)

    @staticmethod
    def init_film(movie_box: FilmBox) -> Pelicula:
        instance = Pelicula()

        instance.directors = movie_box.get_directors()
        instance.titulo = movie_box.get_title()

        return instance


def get_total_films(id_user: int) -> int:

    url = url_FA.URL_USER_PAGE(id_user, 1)
    resp = safe_get_url(url)
    # Guardo la página ya parseada
    soup_page = BeautifulSoup(resp.text, 'lxml')

    # me espero que haya un único "value-box active-tab"
    mydivs = soup_page.find("a", {"class": "value-box active-tab"})
    stringNumber = str(mydivs.contents[3].contents[1])
    # Elimino el punto de los millares
    stringNumber = stringNumber.replace('.', '')
    return int(stringNumber)


def get_all_boxes(user_id: int, total_films: int) -> Iterable[FilmBox]:
    n_pages = ceil(total_films / 20)
    url_pages = (url_FA.URL_USER_PAGE(user_id, i + 1)
                 for i in range(n_pages))

    # Itero todas las páginas del actual usuario
    for page in url_pages:
        # Itero la página actual
        for box in list_boxes(page):
            yield box


def list_boxes(url: str) -> Iterable[FilmBox]:
    resp = safe_get_url(url)
    # Guardo la página ya parseada
    soup_page = BeautifulSoup(resp.text, 'lxml')
    # Leo todas las películas que haya en ella
    return (FilmBox(parsed_box) for parsed_box in
            soup_page.findAll("div", {"class": "user-ratings-movie"}))