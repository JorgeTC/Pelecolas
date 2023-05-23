import pytest

from src.aux_res_directory import get_test_res_folder
from src.essays.html.quoter import Quoter


def get_file_content(file_name: str) -> str:
    res_file_path = get_test_res_folder("quoter_title", file_name)
    with open(res_file_path, encoding='utf-8') as f:
        return f.read()


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
def Johnny() -> str:
    return get_file_content("twice_same_title.txt")


def test_not_quote_twice_same_title(Johnny: str):
    quoter = Quoter("", "")
    quoted_parr = quoter.quote_parr(Johnny)

    # Obtengo las dos frases del archivo
    sentences = Johnny.split(".")

    # Compruebo que se haya citado la segunda vez
    assert sentences[1] not in quoted_parr
    # Compruebo que no se haya citado la primera
    assert sentences[0] in quoted_parr


@pytest.fixture
def Joker() -> str:
    return get_file_content("exactly_but_year.txt")


def test_exactly_but_year(Joker: str):
    quoter = Quoter("", "")
    quoted_parr = quoter.quote_parr(Joker)

    # Compruebo que se haya añadido la cita
    assert quoted_parr != Joker


def test_exactly_but_year_self(Joker: str):
    quoter = Quoter("Joker (2019)", "")
    quoted_parr = quoter.quote_parr(Joker)

    # Compruebo que se no haya añadido la cita
    assert quoted_parr == Joker
