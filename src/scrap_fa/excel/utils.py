from enum import IntFlag, auto

from src.config import Config, Param, Section
from src.pelicula import FAType, Pelicula


def read_film(film: Pelicula) -> Pelicula:
    # Hacemos la parte más lenta, que necesita parsear la página.
    film.get_nota_FA()
    film.get_votantes_FA()
    film.get_duracion()
    film.get_desvest()
    film.get_prop_aprobados()

    return film


class FilmValid(IntFlag):
    # Necesito un bit para las películas que no tengan ningún tipo
    FILM = auto()

    # Un bit para cada tipo que recoge FilmAffinity
    ANIMATION = auto()
    CONCERT = auto()
    DOCUMENTAL = auto()
    EPISODE = auto()
    INTERACTIVE = auto()
    MEDIA = auto()
    MUSIC_VIDEO = auto()
    SHORT_FILM = auto()
    TV_FILM = auto()
    TV_MINISERIES = auto()
    TV_SERIES = auto()
    TV_SHOW = auto()


# Compruebo que FilmValid esté bien definido.
# Necesito que todos los elementos de FAType tengan su correspondiente
assert {item.name for item in FilmValid if item.name != "FILM"} ==\
       {item.name for item in FAType}


def is_valid(film: Pelicula, *,
             SET_VALID_FILM=Config.get_int(Section.READDATA, Param.FILTER_FA)) -> bool:
    """
    Busca en el título que sea una película realmente
    """
    film.get_FA_type()

    # Itero todos los tipos que tiene
    for FA_type in film.FA_type:
        # Compruebo si el tipo invalida la película
        return FilmValid[FA_type.name] & SET_VALID_FILM
    # No se ha encontrado ningún tipo, luego es una película
    return SET_VALID_FILM & FilmValid.FILM
