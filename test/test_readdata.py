from unittest import mock

import pytest

import src.scrap_fa.excel.read_watched.read_watched as rw
from src.scrap_fa.excel.film_box import FilmBox
from src.scrap_fa.excel.read_watched import read_data, read_directors
from src.scrap_fa.excel.read_watched.read_data_watched import ReadDataWatched
from src.scrap_fa.excel.utils import FilmValid, is_valid


@pytest.fixture
def sasha_id() -> int:
    return 1230513


@pytest.fixture
def sasha_total_films() -> int:
    return 35


@pytest.fixture
def sashas_film_boxes(sasha_id, sasha_total_films) -> list[FilmBox]:
    return list(rw.get_all_boxes(sasha_id, sasha_total_films))


def test_read_total_films(sasha_id: int, sasha_total_films: int):
    total_films = rw.get_total_films(sasha_id)
    assert total_films == sasha_total_films
    boxes = list(rw.get_all_boxes(sasha_id, total_films))
    assert len(boxes) == sasha_total_films


def test_from_movie_box(sashas_film_boxes: list[FilmBox]):
    films = (ReadDataWatched.init_film(box) for box in sashas_film_boxes)
    efecto_mariposa = next(film for film in films
                           if film.titulo == 'El efecto mariposa')
    assert efecto_mariposa.user_note == 2
    assert efecto_mariposa.id == 235464


def test_read_data_from_box(sashas_film_boxes: list[FilmBox]):
    efecto_mariposa = next(box for box in sashas_film_boxes
                           if box.get_title() == 'El efecto mariposa')
    assert efecto_mariposa.get_directors() == ['Eric Bress',
                                               'J. Mackye Gruber']
    assert efecto_mariposa.get_country() == 'Estados Unidos'
    assert efecto_mariposa.get_year() == 2004


def all_films_valid():
    return mock.patch.object(is_valid, "__kwdefaults__",
                             {'SET_VALID_FILM': sum(FilmValid)})


@all_films_valid()
@mock.patch.object(ReadDataWatched.read_watched, "__kwdefaults__", {'use_multithread': True})
def test_readdata_parallel(sasha_id: int, sasha_total_films: int):
    sasha_films = list(read_data(sasha_id))
    assert len(sasha_films) == sasha_total_films


@all_films_valid()
@mock.patch.object(ReadDataWatched.read_watched, "__kwdefaults__", {'use_multithread': False})
def test_readdata_series(sasha_id: int):
    watched_in_series = read_data(sasha_id)
    film, proportion = next(watched_in_series)
    assert film is not None
    assert proportion != 0


@all_films_valid()
def test_read_directors(sasha_id: int, sasha_total_films: int):
    watched = list(read_directors(sasha_id))
    assert len(watched) == sasha_total_films
    proportion = watched[-1][1]
    assert proportion == 1
