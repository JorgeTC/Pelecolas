from unittest import mock

import pytest
from bs4 import BeautifulSoup

import src.excel.read_watched_imp as rw
from src.excel.read_watched import read_watched
from src.excel.film_box import FilmBox
from src.excel.utils import is_valid


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
    films = (rw.ReadDataWatched.init_film(box) for box in sashas_film_boxes)
    efecto_mariposa = next(film for film in films
                           if film.titulo == 'El efecto mariposa ')
    assert efecto_mariposa.user_note == 2
    assert efecto_mariposa.id == 235464


def test_read_data_from_box(sashas_film_boxes: list[FilmBox]):
    efecto_mariposa = next(box for box in sashas_film_boxes
                           if box.get_title() == 'El efecto mariposa ')
    assert efecto_mariposa.get_directors() == [
        'Eric Bress', 'J. Mackye Gruber']
    assert efecto_mariposa.get_country() == 'Estados Unidos'
    assert efecto_mariposa.get_year() == 2004


@mock.patch.object(is_valid, "__kwdefaults__", {'SET_VALID_FILM': 255})
@mock.patch.object(rw.ReadDataWatched.read_watched, "__kwdefaults__", {'use_multithread': True})
def test_readdata_parallel(sasha_id: int, sasha_total_films: int):
    sasha_films = list(read_watched(sasha_id))
    assert len(sasha_films) == sasha_total_films


@mock.patch.object(is_valid, "__kwdefaults__", {'SET_VALID_FILM': 255})
@mock.patch.object(rw.ReadDataWatched.read_watched, "__kwdefaults__", {'use_multithread': False})
def test_readdata_series(sasha_id: int):
    watched_in_series = read_watched(sasha_id)
    film, proportion = next(watched_in_series)
    assert film is not None
    assert proportion != 0
