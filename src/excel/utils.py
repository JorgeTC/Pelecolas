from collections import namedtuple

from src.config import Config, Param, Section
from src.pelicula import Pelicula

FilmData = namedtuple("FilmData",
                      ("user_note",
                       "titulo",
                       "id",
                       "duracion",
                       "nota_FA",
                       "votantes_FA",
                       "desvest_FA",
                       "prop_aprobados"))


def read_film(film: Pelicula) -> Pelicula:
    # Hacemos la parte más lenta, que necesita parsear la página.
    film.get_nota_FA()
    film.get_votantes_FA()
    film.get_duracion()
    film.get_desvest()
    film.get_prop_aprobados()
    film.get_director()

    return film

    # Extraemos los datos que usaremos para que el objeto sea más pequeño
    return FilmData(film.user_note,
                    film.titulo,
                    film.id,
                    film.duracion,
                    film.nota_FA,
                    film.votantes_FA,
                    film.desvest_FA,
                    film.prop_aprobados)


def is_valid(film: Pelicula, *,
             SET_VALID_FILM=Config.get_int(Section.READDATA, Param.FILTER_FA)) -> bool:
    """
    Busca en el título que sea una película realmente
    """
    film.get_title()

    # Comprobamos que no tenga ninguno de los sufijos a evitar
    # Filtro los cortos
    if film.titulo.find("(C)") > 0:
        return SET_VALID_FILM & (1 << 5)
    # Excluyo series de televisión
    if film.titulo.find("(Miniserie de TV)") > 0:
        return SET_VALID_FILM & (1 << 4)
    if film.titulo.find("(Serie de TV)") > 0:
        return SET_VALID_FILM & (1 << 3)
    if film.titulo.find("(TV)") > 0:
        # Hay varios tipos de películas aquí.
        # Algunos son programas de televisión, otros estrenos directos a tele.
        # Hay también episodios concretos de series.
        return SET_VALID_FILM & (1 << 2)
    # Filtro los videos musicales
    if film.titulo.find("(Vídeo musical)") > 0:
        return SET_VALID_FILM & (1 << 1)
    # No se ha encontrado sufijo, luego es una película
    return SET_VALID_FILM & (1 << 0)
