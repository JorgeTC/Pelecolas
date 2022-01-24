import math
import re

from bs4 import BeautifulSoup

from src.dlg_config import CONFIG
from src.safe_url import safe_get_url
from src.url_FA import URL_FILM_ID


def get_id_from_url(url):
    # Cojo los 6 dígitos que están después de la palabra film
    str_id = re.search(r"film(\d{6}).html", url).group(1)

    return str_id


SET_VALID_FILM = CONFIG.get_int(CONFIG.S_READDATA, CONFIG.P_FILTER_FA)
def es_valida(titulo):
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

class Pelicula(object):
    def __init__(self, movie_box=None, id=None, urlFA=None):

        self.titulo = ""
        self.user_note = ""
        self.id = ""
        self.url_FA = ""
        self.url_image = ""

        if movie_box:
            self.titulo = self.__get_title(movie_box)
            self.user_note = self.__get_user_note(movie_box)
            self.id = self.__get_id(movie_box)
            self.url_FA = URL_FILM_ID(self.id)
        elif id:
            self.id = str(id)
            self.url_FA = URL_FILM_ID(self.id)
        elif urlFA:
            self.url_FA = str(urlFA)
            self.id = get_id_from_url(self.url_FA)

        self.parsed_page = None
        self.nota_FA = 0
        self.votantes_FA = 0
        self.desvest_FA = 0
        self.values = []
        self.duracion = 0
        self.director = ""
        self.año = None
        self.pais = ""
        self.__exists = bool()

    def __get_title(self, film_box):
        return film_box.contents[1].contents[1].contents[3].contents[1].contents[0].contents[0]

    def __get_user_note(self, film_box):
        return film_box.contents[3].contents[1].contents[1].contents[0]

    def __get_id(self, film_box):
        return film_box.contents[1].contents[1].attrs['data-movie-id']

    def get_nota_FA(self):
        # Obtengo la lista
        self.get_values()

        if self.values:
            # Multiplico la nota por la cantidad de gente que la ha dado
            for vote, quantity in enumerate(self.values):
                self.nota_FA += (vote + 1) * quantity
            # Divido entre el número total
            self.nota_FA /= sum(self.values)
        else:
            self.nota_FA = 0

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

    def get_country(self):

        if not self.parsed_page:
            self.get_parsed_page()

        try:
            self.pais = self.parsed_page.find(
                id="country-img").contents[0].attrs['alt']
        except:
            # caso en el que no está escrita la duración
            self.pais = ""

    def valid(self):
        return es_valida(self.titulo)

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
        # Método que obtiene datos que necesitan parsear la ficha de la película
        # Me aseguro de que esté parseada
        if not self.parsed_page:
            self.get_parsed_page()

        # Llamo a las funciones que leen la ficha parseada
        self.get_nota_FA()
        self.get_votantes_FA()
        self.get_duracion()
        self.get_desvest()

    def get_director(self):

        if not self.parsed_page:
            self.get_parsed_page()

        l = self.parsed_page.find(itemprop="director")
        self.director = l.contents[0].contents[0].contents[0]

    def get_año(self):

        if not self.parsed_page:
            self.get_parsed_page()

        l = self.parsed_page.find(itemprop="datePublished")
        self.año = l.contents[0]

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

    def get_image_url(self):

        if not self.parsed_page:
            self.get_parsed_page()

        self.url_image = self.parsed_page.find("meta", property="og:image")

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

    def exists(self):
        return self.__exists
