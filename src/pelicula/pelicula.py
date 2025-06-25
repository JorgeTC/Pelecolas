import math
import re
from functools import wraps
from typing import Callable

from autoslot import assignments_to_self

from .film_page import FAType, FilmPage


def get_id_from_url(url: str) -> int:
    # Cojo los 6 dígitos que están después de la palabra film
    str_id = re.search(r"film(\d{6}).html", url).group(1)

    return int(str_id)


def assignment_to_self(method: Callable) -> str:
    # Miro los atributos de self que se han escrito dentro del método
    assignments = assignments_to_self(method)
    # Necesito que haya exactamente uno
    if len(assignments) != 1:
        raise AttributeError
    # Devuvlo el único atributo que se ha modificado dentro del método
    return assignments.pop()


def scrap_data(fn: Callable[['Pelicula'], None], attr: str | None = None):
    '''
    Decorador para obtener datos parseados de la página.
    Comprueba que no se haya ya leído el dato para evitar redundancia.
    Comprueba antes de buscar en la página que ya esté parseada.
    '''
    attr = attr or assignment_to_self(fn)

    @wraps(fn)
    def wrp(self: 'Pelicula'):
        # Si ya tengo guardado el dato que se me pide, no busco nada más
        if getattr(self, attr) is not None:
            return

        # Antes de obtener el dato me aseguro de que la página haya sido parseada
        if not self.film_page:
            self.get_parsed_page()

        fn(self)
    return wrp


def check_votes(fn: Callable[['Pelicula'], None], attr: str | None = None):
    attr = attr or assignment_to_self(fn)

    @wraps(fn)
    def wrp(self: 'Pelicula'):
        # Compruebo que haya leído los votos de la película
        if self.values is None:
            self.get_values()

        # Si a pesar de haberlos buscado no he conseguido los votos, no puedo saber su nota
        # por lo tanto no puedo calcular el atributo actual
        if not self.values:
            setattr(self, attr, 0)
            return

        # Tengo los datos que necesito para calcular el atributo en cuestión
        fn(self)
    return wrp


def scrap_from_values(fn: Callable[['Pelicula'], None]):
    '''
    Concatena el decorador para no calcular un atributo dos veces
    y el decorador para comprobar que se tienen los valores
    '''
    # Tengo que obtener attr en este punto porque scrap_data no recibirá la función original.
    # Leerá check_votes, donde no encontrará la asignación que busca
    attr = assignment_to_self(fn)
    # Aplico primero el decorador para evitar calcular el atributo dos veces.
    # Una vez que sé que tengo que estoy obligado a calcular el atributo,
    # compruebo que la lista de valores esté calculada.
    return scrap_data(check_votes(fn, attr), attr)


URL_FILM_ID = "https://www.filmaffinity.com/us/film{}.html".format


class Pelicula:
    def __init__(self):

        self.titulo: str | None = None
        self.user_note: int | None = None
        self.id: int | None = None
        self.url_FA: str | None = None
        self.url_image: str | None = None
        self.film_page: FilmPage | None = None
        self.nota_FA: float | None = None
        self.votantes_FA: int | None = None
        self.desvest_FA: float | None = None
        self.prop_aprobados: float | None = None
        self.values: list[int] | None = None
        self.duracion: int | None = None
        self.directors: list[str] | None = None
        self.año: int | None = None
        self.pais: str | None = None
        self.FA_type: set[FAType] | None = None

    @classmethod
    def from_id(cls, id: int) -> 'Pelicula':
        # Creo el objeto
        instance = cls()

        # Guardo los valores que conozco por la información introducida
        instance.id = int(id)
        instance.url_FA = URL_FILM_ID(instance.id)

        # Devuelvo la instancia
        return instance

    @classmethod
    def from_fa_url(cls, urlFA: str) -> 'Pelicula':
        # Creo el objeto
        instance = cls()

        # Guardo los valores que conozco por la información introducida
        instance.url_FA = urlFA
        instance.id = get_id_from_url(instance.url_FA)

        # Devuelvo la instancia
        return instance

    @scrap_from_values
    def get_nota_FA(self):
        self.nota_FA = 0
        # Multiplico la nota por la cantidad de gente que la ha dado
        for vote, quantity in enumerate(self.values):
            self.nota_FA += (vote + 1) * quantity
        # Divido entre el número total
        self.nota_FA /= sum(self.values)

    @scrap_data
    def get_votantes_FA(self):
        self.votantes_FA = self.film_page.get_votantes_FA()

    @scrap_data
    def get_duracion(self):
        self.duracion = self.film_page.get_duracion()

    @scrap_data
    def get_country(self):
        self.pais = self.film_page.get_country()

    @scrap_data
    def get_title(self):
        self.titulo = self.film_page.get_title()

    def get_parsed_page(self):
        self.film_page = FilmPage(self.url_FA)

    @scrap_data
    def get_director(self):
        self.directors = self.film_page.get_director()

    @scrap_data
    def get_año(self):
        self.año = self.film_page.get_año()

    @scrap_data
    def get_values(self):
        self.values = self.film_page.get_values()

    @scrap_data
    def get_image_url(self):
        self.url_image = self.film_page.get_image_url()

    @scrap_from_values
    def get_desvest(self):

        # Me aseguro que se haya tratado de calcular la nota
        if self.nota_FA is None:
            self.get_nota_FA()

        # Calculo la varianza
        varianza = 0
        # Itero las frecuencias.
        # Cada frecuencia representa a la puntuación igual a su posición en la lista más 1
        for note, votes in enumerate(self.values):
            varianza += votes * ((note + 1 - self.nota_FA) ** 2)
        varianza /= sum(self.values)

        # Doy el valor a la variable miembro, lo convierto a desviación típica
        self.desvest_FA = math.sqrt(varianza)

    @scrap_from_values
    def get_prop_aprobados(self):
        # Cuento cuántos votos positivos hay
        positives = sum(self.values[5:])
        # Cuento cuántos votos hay en total
        total_votes = sum(self.values)
        # Calculo la proporción
        self.prop_aprobados = positives / total_votes

    @scrap_data
    def get_FA_type(self):
        self.FA_type = self.film_page.get_FA_type()

    def exists(self) -> bool:
        return self.film_page.exists

    @property
    def director(self) -> str:
        if self.directors is None:
            return None
        try:
            return self.directors[0]
        except IndexError:
            return ''

    @director.setter
    def director(self, value: str):
        self.directors = [value]
