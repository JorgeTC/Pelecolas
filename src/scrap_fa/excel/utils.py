from src.config import Config, Param, Section
from src.pelicula import Pelicula


def read_film(film: Pelicula) -> Pelicula:
    # Hacemos la parte más lenta, que necesita parsear la página.
    film.get_nota_FA()
    film.get_votantes_FA()
    film.get_duracion()
    film.get_desvest()
    film.get_prop_aprobados()

    return film


def is_valid(film: Pelicula, *,
             SET_VALID_FILM=Config.get_int(Section.READDATA, Param.FILTER_FA)) -> bool:
    """
    Busca en el título que sea una película realmente
    """
    film.get_title()

    # Comprobamos que no tenga ninguno de los sufijos a evitar
    # Filtro los cortos
    if "(C)" in film.titulo:
        return SET_VALID_FILM & (1 << 5)
    # Excluyo series de televisión
    if "(Miniserie de TV)" in film.titulo:
        return SET_VALID_FILM & (1 << 4)
    if "(Serie de TV)" in film.titulo:
        return SET_VALID_FILM & (1 << 3)
    if "(TV)" in film.titulo:
        # Hay varios tipos de películas aquí.
        # Algunos son programas de televisión, otros estrenos directos a tele.
        # Hay también episodios concretos de series.
        return SET_VALID_FILM & (1 << 2)
    # Filtro los videos musicales
    if "(Vídeo musical)" in film.titulo:
        return SET_VALID_FILM & (1 << 1)
    # No se ha encontrado sufijo, luego es una película
    return SET_VALID_FILM & (1 << 0)
