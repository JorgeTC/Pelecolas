from collections import namedtuple

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


def read_film(film: Pelicula) -> FilmData:
    # Hacemos la parte más lenta, que necesita parsear la página.
    film.get_nota_FA()
    film.get_votantes_FA()
    film.get_duracion()
    film.get_desvest()
    film.get_prop_aprobados()

    # Extraemos los datos que usaremos para que el objeto sea más pequeño
    return FilmData(film.user_note,
                    film.titulo,
                    film.id,
                    film.duracion,
                    film.nota_FA,
                    film.votantes_FA,
                    film.desvest_FA,
                    film.prop_aprobados)
