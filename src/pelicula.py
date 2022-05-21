import math
import re

from bs4 import BeautifulSoup
from functools import wraps

from src.config import Config, Section, Param
from src.safe_url import safe_get_url
from src.url_FA import URL_FILM_ID


def get_id_from_url(url: str) -> int:
    # Cojo los 6 dígitos que están después de la palabra film
    str_id = re.search(r"film(\d{6}).html", url).group(1)

    return int(str_id)


SET_VALID_FILM = Config.get_int(Section.READDATA, Param.FILTER_FA)
def es_valida(titulo: str) -> bool:
    """
    Busca en el título que sea una película realmente
    """
    # Comprobamos que no tenga ninuno de los sufijos a evitar
    # Filtro los cortos
    if titulo.find("(C)") > 0:
        return SET_VALID_FILM & (1 << 5)
    # Excluyo series de televisión
    if titulo.find("(Miniserie de TV)") > 0:
        return SET_VALID_FILM & (1 << 4)
    if titulo.find("(Serie de TV)") > 0:
        return SET_VALID_FILM & (1 << 3)
    if titulo.find("(TV)") > 0:
        # Hay varios tipos de películas aquí.
        # Algunos son programas de televisón, otros estrenos directos a tele.
        # Hay también episosios concretos de series.
        return SET_VALID_FILM & (1 << 2)
    # Filtro los videos musicales
    if titulo.find("(Vídeo musical)") > 0:
        return SET_VALID_FILM & (1 << 1)
    # No se ha encontrado sufijo, luego es una película
    return SET_VALID_FILM & (1 << 0)


# Cómo debo buscar la información de las barras
RATING_BARS_PATTERN = re.compile(r'RatingBars.*?\[(.*?)\]')

# Funciones para extraer datos de la caja de la película
def get_title_from_film_box(film_box: BeautifulSoup) -> str:
    return film_box.contents[1].contents[1].contents[3].contents[1].contents[0].contents[0]


def get_user_note_from_film_box(film_box: BeautifulSoup) -> int:
    return int(film_box.contents[3].contents[1].contents[1].contents[0])


def get_id_from_film_box(film_box: BeautifulSoup) -> int:
    return int(film_box.contents[1].contents[1].attrs['data-movie-id'])


def scrap_data(att: str):
    '''
    Decorador para obtener datos parseados de la página.
    Comprueba que no se haya ya leído el dato para evitar redundancia.
    Comprueba antes de buscar en la página que ya esté parseada.
    '''
    def decorator(fn):

        @wraps(fn)
        def wrp(*args, **kwarg):
            # Me guardo la instancia
            self: 'Pelicula' = args[0]

            # Si ya tengo guardado el dato que se me pide, no busco nada más
            if getattr(self, att) is not None:
                return

            # Antes de obtener el dato me aseguro de que la página haya sido parseada
            if not self.parsed_page:
                self.get_parsed_page()

            fn(*args, **kwarg)
            pass

        return wrp

    return decorator

class Pelicula():
    def __init__(self):

        self.titulo: str = None
        self.user_note: int = None
        self.id: int = None
        self.url_FA: str = None
        self.url_image: str = None
        self.parsed_page: BeautifulSoup = None
        self.nota_FA: float = None
        self.votantes_FA: int = None
        self.desvest_FA: float = None
        self.values: list[int] = None
        self.duracion: int = 0
        self.director: str = None
        self.año: int = None
        self.pais: str = None
        self.__exists: bool = None

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
        instance.url_FA = str(urlFA)
        instance.id = get_id_from_url(instance.url_FA)

        # Devuelvo la instancia
        return instance

    @classmethod
    def from_movie_box(cls, movie_box: BeautifulSoup) -> 'Pelicula':
        # Creo el objeto
        instance = cls()

        # Guardo los valores que conozco por la información introducida
        instance.titulo = get_title_from_film_box(movie_box)
        instance.user_note = get_user_note_from_film_box(movie_box)
        instance.id = get_id_from_film_box(movie_box)
        instance.url_FA = URL_FILM_ID(instance.id)

        # Devuelvo la instancia
        return instance

    @scrap_data('nota_FA')
    def get_nota_FA(self):

        # Doy valor inicial a la nota
        self.nota_FA = 0

        # Obtengo la lista
        self.get_values()
        # Si no la consigo, salgo
        if not self.values:
            return

        # Multiplico la nota por la cantidad de gente que la ha dado
        for vote, quantity in enumerate(self.values):
            self.nota_FA += (vote + 1) * quantity
        # Divido entre el número total
        self.nota_FA /= sum(self.values)

    @scrap_data('votantes_FA')
    def get_votantes_FA(self):
        # Me espero que la página ya haya sido parseada
        l = self.parsed_page.find(itemprop="ratingCount")
        try:
            # guardo la cantidad de votantes en una ficha normal
            self.votantes_FA = l.attrs['content']
            # Elimino el punto de los millares
            self.votantes_FA = self.votantes_FA.replace('.', '')
            self.votantes_FA = int(self.votantes_FA)
        except:
            # caso en el que no hay suficientes votantes
            self.votantes_FA = 0

    @scrap_data('duracion')
    def get_duracion(self):
        # Me espero que la página ya haya sido parseada
        l = self.parsed_page.find(id="left-column")
        try:
            str_duracion = l.find(itemprop="duration").contents[0]
            str_duracion = re.search(r'(\d+) +min.', str_duracion).group(1)
            self.duracion = int(str_duracion)
        except:
            # caso en el que no está escrita la duración
            self.duracion = 0

    @scrap_data('pais')
    def get_country(self):
        try:
            self.pais = self.parsed_page.find(
                id="country-img").contents[0].attrs['alt']
        except:
            return

    def valid(self) -> bool:
        if not self.titulo:
            self.get_title()
        return es_valida(self.titulo)

    @scrap_data('titulo')
    def get_title(self):

        l = self.parsed_page.find(itemprop="name")
        self.titulo = l.contents[0]

    def get_parsed_page(self):
        resp = safe_get_url(self.url_FA)
        if resp.status_code == 404:
            self.__exists = False
            # Si el id no es correcto, dejo de construir la clase
            return
        self.__exists = True

        # Parseo la página
        self.parsed_page = BeautifulSoup(resp.text, 'html.parser')

    def get_time_and_FA(self):

        # Llamo a las funciones que leen la ficha parseada
        self.get_nota_FA()
        self.get_votantes_FA()
        self.get_duracion()
        self.get_desvest()

    @scrap_data('director')
    def get_director(self):

        l = self.parsed_page.find(itemprop="director")
        self.director = l.contents[0].contents[0].contents[0]

    @scrap_data('año')
    def get_año(self):

        l = self.parsed_page.find(itemprop="datePublished")
        self.año = l.contents[0]

    @scrap_data('values')
    def get_values(self):
        # Recopilo los datos específicos de la varianza:
        script = self.parsed_page.find("script", text=RATING_BARS_PATTERN)
        if script:
            bars = script.string
        else:
            return

        # Extraigo cuánto vale cada barra
        bars = RATING_BARS_PATTERN.search(bars).group(1)
        self.values = [int(s) for s in bars.split(',')]
        # Las ordeno poniendo primero las notas más bajas
        self.values.reverse()
        # Me aseguro que todos los datos sean positivos
        self.values = [max(value, 0) for value in self.values]

    @scrap_data('url_image')
    def get_image_url(self):

        self.url_image = self.parsed_page.find(
            "meta", property="og:image")['content']

    @scrap_data('desvest_FA')
    def get_desvest(self):

        if not self.values:
            self.get_values()

        # Me espero que antes de llamar a esta función ya se haya llamado
        # a la función para buscar la nota de FA
        if self.nota_FA == 0:
            self.desvest_FA = 0
            return

        # Calculo la varianza
        varianza = 0
        # Itero las frecuencias.
        # Cada frecuencia representa a la puntuación igual a su posición en la lista más 1
        for note, votes in enumerate(self.values):
            varianza += votes * ((note + 1 - self.nota_FA) ** 2)
        varianza /= sum(self.values)

        # Doy el valor a la variable miembro, lo convierto a desviación típica
        self.desvest_FA = math.sqrt(varianza)

    def exists(self) -> bool:
        return self.__exists
