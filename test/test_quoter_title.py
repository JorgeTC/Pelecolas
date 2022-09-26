import pytest
from src.aux_res_directory import get_test_res_folder
from src.quoter import Quoter


def get_file_content(file_name: str) -> str:
    res_file_path = get_test_res_folder("quoter_title", file_name)
    return open(res_file_path, encoding='utf-8').read()


@pytest.fixture
def VerbenaDeLaPaloma() -> str:
    return get_file_content("own_not_exactly_title.txt")


def test_not_quote_own_title(VerbenaDeLaPaloma: str):
    quoter = Quoter("La verbena de la Paloma", "")
    quoted_parr = quoter.quote_parr(VerbenaDeLaPaloma)

    assert quoted_parr == VerbenaDeLaPaloma


def test_not_quote_own_title_not_exact(VerbenaDeLaPaloma: str):
    quoter = Quoter("La verbena de la Paloma (1935)", "")
    quoted_parr = quoter.quote_parr(VerbenaDeLaPaloma)

    assert quoted_parr == VerbenaDeLaPaloma


@pytest.fixture
def VerbenaDeLaPaloma1935() -> str:
    return get_file_content("own_not_exactly_title.txt")


def test_not_quote_own_title_year(VerbenaDeLaPaloma1935: str):
    quoter = Quoter("La verbena de la Paloma", "")
    quoted_parr = quoter.quote_parr(VerbenaDeLaPaloma1935)

    assert quoted_parr == VerbenaDeLaPaloma1935


def test_not_quote_own_title_not_exact_year(VerbenaDeLaPaloma1935: str):
    quoter = Quoter("La verbena de la Paloma (1935)", "")
    quoted_parr = quoter.quote_parr(VerbenaDeLaPaloma1935)

    assert quoted_parr == VerbenaDeLaPaloma1935


@pytest.fixture
def Joker() -> str:
    return get_file_content("twice_same_title.txt")


def test_not_quote_twice_same_title(Joker: str):
    quoter = Quoter("", "")
    quoted_parr = quoter.quote_parr(Joker)

    # Obtengo las dos frases del archivo
    sentences = Joker.split(".")

    # Compruebo que se haya citado la segunda vez
    assert quoted_parr.find(sentences[1]) == -1
    # Compruebo que no se haya citado la primera
    assert quoted_parr.find(sentences[0]) > -1
