import pytest
from unittest import mock

from src.aux_res_directory import get_res_folder
from src.quoter import Quoter


def get_file_content(file_name: str) -> str:
    res_file_path = get_res_folder("tests", "quoter", file_name)
    return open(res_file_path, encoding='utf-8').read()


@pytest.fixture
def TarantinoParr() -> str:
    return get_file_content("twice_same_director.txt")


def test_quote_title_without_dlg(TarantinoParr: str):
    quoter = Quoter("", "")
    parr = quoter.quote_parr(TarantinoParr)

    # Compruebo que haya citado a Tarantino
    assert "Quentin Tarantino" in quoter._Quoter__quoted_directors

    sentences = TarantinoParr.split(".")
    # Compruebo que se haya citado la primera aparición
    assert parr.find(sentences[0]) == -1
    # Compruebo que no se ha citado la segunda aparición
    assert parr.find(sentences[1]) > -1

    # Paso el mismo párrafo.
    # No quiero que ahora cite a Tarantino
    parr = quoter.quote_parr(TarantinoParr)
    assert parr == TarantinoParr


def test_not_quote_same_director(TarantinoParr: str):
    quoter = Quoter("", "Quentin Tarantino")
    quoted_parr = quoter.quote_parr(TarantinoParr)

    # Compruebo que haya citado a Tarantino
    assert "Quentin Tarantino" not in quoter._Quoter__quoted_directors

    # Compruebo que no se haya modificado el texto
    assert quoted_parr == TarantinoParr


@pytest.fixture
def Bergman() -> str:
    return get_file_content("ask.txt")


def test_quote_director_with_dlg(Bergman: str):
    # Si Ingmar Bergman no está, este test no sirve
    assert "Ingmar Bergman" in Quoter.ALL_DIRECTORS
    # tampoco puede estar la palabra Bergman como uno de los directores de confianza
    assert "Bergman" not in Quoter.TRUST_DIRECTORS

    quoter = Quoter("", "")
    # Compruebo que se haya preguntado al usuario por Bergman
    with mock.patch('builtins.input', return_value="Sí") as mock_confirmation:
        quoted_parr = quoter.quote_parr(Bergman)
        assert mock_confirmation.call_count == 1

    # Como el usuario ha contestado que sí, se comprueba que se haya hecho la cita
    assert "Ingmar Bergman" in quoter._Quoter__quoted_directors
    assert quoted_parr != Bergman


def test_not_quote_director_with_dlg(Bergman: str):
    # Si Ingmar Bergman no está, este test no sirve
    assert "Ingmar Bergman" in Quoter.ALL_DIRECTORS
    # tampoco puede estar la palabra Bergman como uno de los directores de confianza
    assert "Bergman" not in Quoter.TRUST_DIRECTORS

    quoter = Quoter("", "")
    # Compruebo que se haya preguntado al usuario por Bergman
    with mock.patch('builtins.input', return_value="No") as mock_confirmation:
        quoted_parr = quoter.quote_parr(Bergman)
        assert mock_confirmation.call_count == 1

    # Como el usuario ha contestado que no, se comprueba que se haya hecho la cita
    assert "Ingmar Bergman" not in quoter._Quoter__quoted_directors
    assert quoted_parr == Bergman


@pytest.fixture
def vonTrier() -> str:
    return get_file_content("not_whole_name.txt")


def test_director_more_than_one_word_not_complete_name(vonTrier: str):
    # Me espero que von Trier esté como director a citar siempre
    assert "von Trier" in Quoter.TRUST_DIRECTORS

    quoter = Quoter("", "")
    with mock.patch('builtins.input', return_value="No") as mock_confirmation:
        quoted_parr = quoter.quote_parr(vonTrier)
        if "von Trier" in Quoter.TRUST_DIRECTORS:
            assert mock_confirmation.call_count == 0
        else:
            assert mock_confirmation.call_count == 1

    # Compruebo que se haya hecho la citación
    assert "Lars von Trier" in quoter._Quoter__quoted_directors
    assert quoted_parr != vonTrier


@pytest.fixture
def Paco() -> str:
    return get_file_content("name_in_title.txt")


'''
def test_not_ask_in_title(Paco: str):
    # Si no hay ningún Paco en los directores, el test no sirve
    assert "Paco Plaza" in Quoter.ALL_DIRECTORS
    # tampoco puede estar la palabra Paco como uno de los directores de confianza
    assert "Paco" not in Quoter.TRUST_DIRECTORS

    quoter = Quoter("", "")
    # Compruebo que no se pregunte por ningún director
    with mock.patch('builtins.input', return_value="No") as mock_confirmation:
        quoted_parr = quoter.quote_parr(Paco)
        assert mock_confirmation.call_count == 0

    assert quoted_parr == Paco
'''


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
