from itertools import pairwise
from test.mocks_non_substitution import MockGeneratorWithoutReplace

from src.essays.searcher import Searcher, search_boxes
from src.pelicula import get_id_from_url


def test_unique_film():
    searcher = Searcher("Mi tío Jacinto")
    assert get_id_from_url(searcher.get_url()) == 736750


def test_unique_film_wrong_year():
    searcher = Searcher("Mi tío Jacinto (1200)")
    assert searcher.get_url() == ""


def test_unique_film_special_chars():
    searcher = Searcher("El milagro de P. Tinto")
    assert get_id_from_url(searcher.get_url()) == 968751

    searcher = Searcher("¿Teléfono rojo? Volamos hacia Moscú")
    assert get_id_from_url(searcher.get_url()) == 479847

    searcher = Searcher("Jo, ¡qué noche!")
    assert get_id_from_url(searcher.get_url()) == 345042


def test_numbers():
    searcher = Searcher("2001: Una odisea del espacio (1968)")
    assert get_id_from_url(searcher.get_url()) == 171099


def test_more_then_one_film_with_same_title():
    searcher = Searcher("La caza")
    assert searcher.has_results()
    assert searcher.get_url() == ""


def test_more_then_one_with_year():
    searcher = Searcher("La caza (1966)")
    assert searcher.has_results()
    assert get_id_from_url(searcher.get_url()) == 399542

    searcher = Searcher("La caza (2012)")
    assert searcher.has_results()
    assert get_id_from_url(searcher.get_url()) == 858945

    # Hay dos películas llamadas "La caza" del año 2015
    searcher = Searcher("La caza (2015)")
    assert searcher.has_results()
    assert searcher.get_url() == ""


def test_not_found():
    searcher = Searcher("La película que no existe")
    assert not searcher.has_results()
    assert searcher.get_url() == ""


def test_not_found_many_results():
    searcher = Searcher("Caza")
    assert searcher.has_results()
    assert searcher.get_url() == ""


def test_not_found_same_year():
    searcher = Searcher("Pinocho (1000)")
    assert searcher.has_results()

    with MockGeneratorWithoutReplace(search_boxes) as mock_search_boxes:
        assert searcher.get_url() == ""
        assert mock_search_boxes.call_count == 1
        assert any(film.año == next_film.año
                   for film, next_film
                   in pairwise(mock_search_boxes.return_values[-1]))


def test_two_results_in_same_year():
    searcher = Searcher("Mean girls")
    assert searcher.has_results()
    assert searcher.get_url() == ""


def test_house_error():
    searcher = Searcher("House (1977)")
    assert searcher.has_results()
    assert searcher.get_url() == ""
