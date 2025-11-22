import logging
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

# Creamos una constante que permite que is_valid devuelva siempre True
# Usada principalmente en tests o cuando se quiere desactivar el filtrado
ALL_FILM_VALID = FilmValid(~0)

# Compruebo que FilmValid esté bien definido.
# Necesito que todos los elementos de FAType tengan su correspondiente
assert {item.name for item in FilmValid if item.name != "FILM"} ==\
       {item.name for item in FAType}


def log_valid_film(valid_film: FilmValid) -> None:
    # Creo el string para el log
    log_string = "Valid film types: "

    # Itero todos los tipos y pongo si son válidos o no
    type_strings = []
    for film_type in FilmValid:
        type_value = 1 if film_type & valid_film else 0
        type_strings.append(f"{film_type.name}={type_value}")
    log_string += ", ".join(type_strings)

    logging.info(log_string)


def load_valid_film() -> FilmValid:
    valid_film = FilmValid(Config.get_int(Section.READDATA, Param.FILTER_FA))

    # Escribe en el log qué tipos de película son válidos
    log_valid_film(valid_film)

    return valid_film


def is_valid(film: Pelicula,
             SET_VALID_FILM=load_valid_film()) -> bool:
    """
    Busca en el título que sea una película realmente
    """
    film.get_FA_type()

    if len(film.FA_type) == 0:
        # No se ha encontrado ningún tipo, luego es una película
        return bool(SET_VALID_FILM & FilmValid.FILM)

    # Itero todos los tipos que tiene
    for FA_type in film.FA_type:
        # Compruebo si el tipo invalida la película
        if not FilmValid[FA_type.name] & SET_VALID_FILM:
            return False
    # Ninguno de sus tipos me invalida esta película
    return True
