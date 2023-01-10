from src.excel.read_watched_imp import ReadDirectorsWatched, ReadDataWatched
from src.pelicula import Pelicula


def read_directors(id_user: int) -> tuple[Pelicula, float]:
    reader = ReadDirectorsWatched(id_user)
    for film in reader.iter():
        yield film, reader.proportion


def read_watched(id_user: int) -> tuple[Pelicula, float]:
    reader = ReadDataWatched(id_user)
    for film in reader.iter():
        yield film, reader.proportion
