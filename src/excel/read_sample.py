from concurrent.futures import Future, ThreadPoolExecutor
from queue import Queue
from random import randint
from threading import Lock, Thread
from typing import Iterable, Optional

from src.config import Config, Param, Section
from src.excel.utils import is_valid, read_film
from src.pelicula import Pelicula


class RandomFilmId:
    def __init__(self) -> None:
        self.ids = list(range(100_000, 1_000_000))
        self.size = len(self.ids)
        self.mutex = Lock()

    def get_id(self) -> int:

        if self.size == 0:
            return 0

        self.size -= 1
        rand_index = randint(0, self.size)
        self.ids[self.size], self.ids[rand_index] = self.ids[rand_index], self.ids[self.size]

        return self.ids.pop()

    def __iter__(self):
        return self

    def __next__(self) -> int:
        with self.mutex:
            if self.size != 0:
                return self.get_id()
            else:
                raise StopIteration


def read_sample() -> Iterable[Pelicula]:
    return ReadSample().iter()


class ReadSample:
    def __init__(self) -> None:
        self.results: Queue[Pelicula] = Queue()

        Thread(target=self.read_sample,
               name="ReadSample").start()

    def add_to_queue(self, result: Future):
        if (film := result.result()):
            self.results.put(film)

    def read_sample(self, *,
                    use_multithread=Config.get_bool(Section.READDATA, Param.PARALLELIZE)) -> Iterable[Pelicula]:

        # Generador de películas con id aleatorio
        film_list = (Pelicula.from_id(film_id) for film_id in RandomFilmId())

        # Obtengo los datos de los id válidos que obtenga
        if use_multithread:
            exe = ThreadPoolExecutor(thread_name_prefix="ReadFilm")
            futures = (exe.submit(read_film_if_valid, film)
                       for film in film_list)
            for future in futures:
                future.add_done_callback(self.add_to_queue)
            exe.shutdown(wait=True)
        else:
            for film in film_list:
                if (read_film := read_film_if_valid(film)):
                    self.results.put(read_film)

        # Añado un elemento None para indicar que la iteración ha acabado
        self.results.put(None)

    def iter(self) -> Iterable[Pelicula]:
        while (film := self.results.get()):
            yield film


def read_film_if_valid(film: Pelicula) -> Optional[Pelicula]:
    if not has_valid_id(film):
        return None
    # Es válida, devuelvo la película con todos los datos necesarios
    try:
        return read_film(film)
    except:
        return None


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
    if not is_valid(film):
        return False

    # Compruebo por último que tenga nota media
    film.get_nota_FA()
    if not film.nota_FA:
        return False

    # Si el id es válido, el título es válido y tiene nota en FA, es un id válido para mi estadística
    return True
