from src.essays.searcher import Searcher
from src.pelicula import get_id_from_url


def test_unique_film():
    searcher = Searcher("Casablanca")
    assert get_id_from_url(searcher.get_url()) == 165208


def test_unique_film_wrong_year():
    searcher = Searcher("Casablanca (1200)")
    assert searcher.get_url() == ""


def test_unique_film_special_chars():
    searcher = Searcher("El milagro de P. Tinto")
    assert get_id_from_url(searcher.get_url()) == 968751


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

    searcher = Searcher("La caza (2015)")
    assert searcher.has_results()
    assert get_id_from_url(searcher.get_url()) == 670127


def test_not_found():
    searcher = Searcher("La película que no existe")
    assert not searcher.has_results()
    assert searcher.get_url() == ""


def test_two_results_in_same_year():
    searcher = Searcher("Mean girls")
    assert searcher.has_results()
    assert searcher.get_url() == ""
