from unittest import mock

import pytest
from src.aux_res_directory import get_res_folder
from src.quoter import Quoter


def get_file_content(file_name: str) -> str:
    res_file_path = get_res_folder("tests", "quoter", file_name)
    return open(res_file_path, encoding='utf-8').read()


@pytest.fixture
def TarantinoParr() -> str:
    return get_file_content("twice_same_director.txt")


@mock.patch.object(Quoter, "ALL_DIRECTORS", {"Quentin Tarantino"})
@mock.patch.object(Quoter, "TRUST_DIRECTORS", {"Tarantino"})
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


@mock.patch.object(Quoter, "ALL_DIRECTORS", {"Quentin Tarantino"})
@mock.patch.object(Quoter, "TRUST_DIRECTORS", {"Tarantino"})
def test_not_quote_same_director(TarantinoParr: str):
    quoter = Quoter("", "Quentin Tarantino")
    quoted_parr = quoter.quote_parr(TarantinoParr)

    # Compruebo que no haya citado a Tarantino
    assert "Quentin Tarantino" not in quoter._Quoter__quoted_directors

    # Compruebo que no se haya modificado el texto
    assert quoted_parr == TarantinoParr


@pytest.fixture
def Bergman() -> str:
    return get_file_content("ask.txt")


@mock.patch.object(Quoter, "ALL_DIRECTORS", {"Ingmar Bergman"})
@mock.patch.object(Quoter, "TRUST_DIRECTORS", {""})
def test_quote_director_with_dlg(Bergman: str):
    quoter = Quoter("", "")
    # Compruebo que se haya preguntado al usuario por Bergman
    with mock.patch('builtins.input', return_value="Sí") as mock_confirmation:
        quoted_parr = quoter.quote_parr(Bergman)
        assert mock_confirmation.call_count == 1

    # Como el usuario ha contestado que sí, se comprueba que se haya hecho la cita
    assert "Ingmar Bergman" in quoter._Quoter__quoted_directors
    assert quoted_parr != Bergman


@mock.patch.object(Quoter, "ALL_DIRECTORS", {"Ingmar Bergman"})
@mock.patch.object(Quoter, "TRUST_DIRECTORS", {""})
def test_not_quote_director_with_dlg(Bergman: str):
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


@mock.patch.object(Quoter, "ALL_DIRECTORS", {"Lars von Trier"})
@mock.patch.object(Quoter, "TRUST_DIRECTORS", {"von Trier"})
def test_director_more_than_one_word_not_complete_name(vonTrier: str):
    quoter = Quoter("", "")

    with mock.patch('builtins.input', return_value="No") as mock_confirmation:
        quoted_parr = quoter.quote_parr(vonTrier)
        assert mock_confirmation.call_count == 0

    # Compruebo que se haya hecho la citación
    assert "Lars von Trier" in quoter._Quoter__quoted_directors
    assert quoted_parr != vonTrier


@pytest.fixture
def Paco() -> str:
    return get_file_content("name_in_title.txt")


'''
@mock.patch.object(Quoter, "ALL_DIRECTORS", {"Paco Plaza"})
@mock.patch.object(Quoter, "TRUST_DIRECTORS", {""})
def test_not_ask_in_title(Paco: str):
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


@pytest.fixture
def SpecialLemma() -> str:
    return get_file_content("pronombre_personal.txt")


@mock.patch.object(Quoter, "ALL_DIRECTORS", {"Joel Coen"})
@mock.patch.object(Quoter, "TRUST_DIRECTORS", {"Coen"})
def test_lemma(SpecialLemma: str):
    quoter = Quoter("", "")
    with mock.patch('builtins.input', return_value="Sí") as mock_confirmation:
        quoted_parr = quoter.quote_parr(SpecialLemma)
        assert mock_confirmation.call_count == 0

    # Compruebo que se haya citado a los Coen
    quoted_directors = {"Joel Coen"}
    assert quoted_directors == quoter._Quoter__quoted_directors
    # El resto de frases no pueden haber cambiado
    ori_sentences = SpecialLemma.split(". ")
    quoted_sentences = quoted_parr.split(". ")
    assert len(ori_sentences) == len(quoted_sentences)
    for i in range(1, len(ori_sentences)):
        assert ori_sentences[i] == quoted_sentences[i]


@pytest.fixture
def Punctuation() -> str:
    return get_file_content("name_with_points.txt")


'''
@mock.patch.object(Quoter, "ALL_DIRECTORS", {"Jose Antonio Bardem", "Jesús Pascual"})
@mock.patch.object(Quoter, "TRUST_DIRECTORS", {""})
def test_director_punctuation(Punctuation: str):
    quoter = Quoter("", "")

    def has_been_asked(name_in_question: str, calls: list[mock._Call]):
        for call in calls:
            args, kwargs = call
            assert len(args) == 1 and len(kwargs) == 0
            question: str = args[0]
            if question.find(name_in_question) > -1:
                return True
        return False

    with mock.patch('builtins.input', return_value="No") as mock_input:
        quoted_parr = quoter.quote_parr(Punctuation)

        # Compruebo que no se haya preguntado por palabras con signos de puntuación
        assert not has_been_asked('Antonio.', mock_input.call_args_list)
        assert not has_been_asked('Jesús?', mock_input.call_args_list)

    assert quoted_parr == Punctuation
'''


@pytest.fixture
def PunctuationNotRecognized() -> str:
    return get_file_content("point_makes_not_recognized.txt")


'''
@mock.patch.object(Quoter, "ALL_DIRECTORS", {"Yorgos Lanthimos"})
@mock.patch.object(Quoter, "TRUST_DIRECTORS", {"Lanthimos"})
def test_recognize_name_with_point(PunctuationNotRecognized: str):
    quoter = Quoter("", "")

    with mock.patch('builtins.input', return_value="Sí"):
        quoted_parr = quoter.quote_parr(PunctuationNotRecognized)

    assert quoted_parr != PunctuationNotRecognized
'''
