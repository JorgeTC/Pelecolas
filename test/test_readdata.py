import pytest
from bs4 import BeautifulSoup
import src.excel.read_watched as rw
from src.excel.read_watched import FromFilmBox


@pytest.fixture
def sasha_id() -> int:
    return 1230513


@pytest.fixture
def sashas_film_boxes(sasha_id) -> list[BeautifulSoup]:
    pages = list(rw.get_all_boxes(sasha_id, 35))
    return sum(pages, [])


def test_read_total_films(sasha_id: int):
    total_films = rw.get_total_films(sasha_id)
    assert total_films == 35
    pages = list(rw.get_all_boxes(sasha_id, total_films))
    assert len(pages) == 35 // 20 + 1
    assert sum(len(page) for page in pages) == 35


def test_from_movie_box(sashas_film_boxes: list[BeautifulSoup]):
    films = (rw.init_film_from_movie_box(box) for box in sashas_film_boxes)
    efecto_mariposa = next(film for film in films
                           if film.titulo == 'El efecto mariposa ')
    assert efecto_mariposa.user_note == 2
    assert efecto_mariposa.id == 235464


def test_read_data_from_box(sashas_film_boxes: list[BeautifulSoup]):
    efecto_mariposa = next(box for box in sashas_film_boxes
                           if FromFilmBox.get_title(box) == 'El efecto mariposa ')
    assert FromFilmBox.get_directors(efecto_mariposa) == [
        'Eric Bress', 'J. Mackye Gruber']
    assert FromFilmBox.get_country(efecto_mariposa) == 'Estados Unidos'
    assert FromFilmBox.get_year(efecto_mariposa) == 2004
