from unittest import mock

import pytest

from src.aux_res_directory import get_test_res_folder
from src.essays.html.quoter import Quoter, QuoterDirector


def get_file_content(file_name: str) -> str:
    res_file_path = get_test_res_folder("quoter_director", file_name)
    with open(res_file_path, encoding='utf-8') as f:
        return f.read()


def mock_ask_confirmation(return_value: bool):
    return mock.patch.object(QuoterDirector, '_QuoterDirector__ask_confirmation', return_value=return_value)


@pytest.fixture
def TarantinoParr() -> str:
    return get_file_content("twice_same_director.txt")


def patch_QuoterDirector(all_directors: set[str], trust_directors: set[str]):

    def decorator(fn):
        if all_directors is not None:
            mock_all_directors = mock.patch.object(
                QuoterDirector.ALL_DIRECTORS, "value", all_directors)
            fn = mock_all_directors(fn)

        if trust_directors is not None:
            mock_trust_directors = mock.patch.object(
                QuoterDirector, "TRUST_DIRECTORS", trust_directors)
            fn = mock_trust_directors(fn)

        return fn

    return decorator


@patch_QuoterDirector({"Quentin Tarantino"}, {"Tarantino"})
def test_quote_title_without_dlg(TarantinoParr: str):
    quoter = Quoter("", "")
    parr = quoter.quote_parr(TarantinoParr)

    # Compruebo que haya citado a Tarantino
    assert "Quentin Tarantino" in quoter.quoted_directors

    sentences = TarantinoParr.split(".")
    # Compruebo que se haya citado la primera aparición
    assert sentences[0] not in parr
    # Compruebo que no se ha citado la segunda aparición
    assert sentences[1] in parr

    # Paso el mismo párrafo.
    # No quiero que ahora cite a Tarantino
    parr = quoter.quote_parr(TarantinoParr)
    assert parr == TarantinoParr


@patch_QuoterDirector({"Quentin Tarantino"}, {"Tarantino"})
def test_not_quote_same_director(TarantinoParr: str):
    quoter = Quoter("", "Quentin Tarantino")
    quoted_parr = quoter.quote_parr(TarantinoParr)

    # Compruebo que no haya citado a Tarantino
    assert "Quentin Tarantino" not in quoter.quoted_directors

    # Compruebo que no se haya modificado el texto
    assert quoted_parr == TarantinoParr


@pytest.fixture
def Bergman() -> str:
    return get_file_content("ask.txt")


@patch_QuoterDirector({"Ingmar Bergman"}, {""})
def test_quote_director_with_dlg(Bergman: str):
    quoter = Quoter("", "")
    # Compruebo que se haya preguntado al usuario por Bergman
    with mock.patch('builtins.input', return_value="Sí") as mock_confirmation:
        quoted_parr = quoter.quote_parr(Bergman)
        assert mock_confirmation.call_count == 1

    # Como el usuario ha contestado que sí, se comprueba que se haya hecho la cita
    assert "Ingmar Bergman" in quoter.quoted_directors
    assert quoted_parr != Bergman


@patch_QuoterDirector({"Ingmar Bergman"}, {""})
def test_not_quote_director_with_dlg(Bergman: str):
    quoter = Quoter("", "")
    # Compruebo que se haya preguntado al usuario por Bergman
    with mock.patch('builtins.input', return_value="No") as mock_confirmation:
        quoted_parr = quoter.quote_parr(Bergman)
        assert mock_confirmation.call_count == 1

    # Como el usuario ha contestado que no, se comprueba que se haya hecho la cita
    assert "Ingmar Bergman" not in quoter.quoted_directors
    assert quoted_parr == Bergman


@pytest.fixture
def vonTrier() -> str:
    return get_file_content("not_whole_name.txt")


@patch_QuoterDirector({"Lars von Trier"}, {"Von Trier"})
def test_director_more_than_one_word_not_complete_name(vonTrier: str):
    quoter = Quoter("", "")

    with mock.patch('builtins.input', return_value="No") as mock_confirmation:
        quoted_parr = quoter.quote_parr(vonTrier)
        assert mock_confirmation.call_count == 0

    # Compruebo que se haya hecho la citación
    assert "Lars von Trier" in quoter.quoted_directors
    assert quoted_parr != vonTrier


@pytest.fixture
def Plaza() -> str:
    return get_file_content("name_in_title.txt")


@patch_QuoterDirector({"Paco Plaza"}, {""})
def test_not_ask_in_title(Plaza: str):
    quoter = Quoter("", "")

    # Compruebo que no se pregunte por ningún director
    with mock.patch('builtins.input', return_value="No") as mock_confirmation:
        quoted_parr = quoter.quote_parr(Plaza)
        assert mock_confirmation.call_count == 0

    assert quoted_parr == Plaza


@pytest.fixture
def SpecialLemma() -> str:
    return get_file_content("pronombre_personal.txt")


@patch_QuoterDirector({"Joel Coen"}, {"Coen"})
def test_lemma(SpecialLemma: str):
    quoter = Quoter("", "")
    with mock.patch('builtins.input', return_value="Sí") as mock_confirmation:
        quoted_parr = quoter.quote_parr(SpecialLemma)
        assert mock_confirmation.call_count == 0

    # Compruebo que se haya citado a los Coen
    quoted_directors = {"Joel Coen"}
    assert quoted_directors == quoter.quoted_directors
    # El resto de frases no pueden haber cambiado
    ori_sentences = SpecialLemma.split(". ")
    quoted_sentences = quoted_parr.split(". ")
    assert len(ori_sentences) == len(quoted_sentences)
    for i in range(1, len(ori_sentences)):
        assert ori_sentences[i] == quoted_sentences[i]


@pytest.fixture
def Punctuation() -> str:
    return get_file_content("name_with_points.txt")


def is_to_be_asked(name_in_question: str, mock: mock.MagicMock) -> bool:
    calls = mock.call_args_list
    for call in calls:
        args, kwargs = call
        try:
            name = kwargs['name']
        except KeyError:
            name = args[0]
        if name_in_question == name:
            return True
    return False


@patch_QuoterDirector({"Jose Antonio Bardem", "Jesús Pascual"}, {""})
def test_director_punctuation(Punctuation: str):
    quoter = Quoter("", "")

    with mock_ask_confirmation(False) as mock_input:
        quoted_parr = quoter.quote_parr(Punctuation)

        # Compruebo que no se haya preguntado por palabras con signos de puntuación
        assert not is_to_be_asked('Antonio.', mock_input)
        assert not is_to_be_asked('Jesús?', mock_input)

    assert quoted_parr == Punctuation


@pytest.fixture
def PunctuationNotRecognized() -> str:
    return get_file_content("point_makes_not_recognized.txt")


@patch_QuoterDirector({"Yorgos Lanthimos"}, {"Lanthimos"})
def test_recognize_name_with_point(PunctuationNotRecognized: str):
    quoter = Quoter("", "")

    with mock_ask_confirmation(True):
        quoted_parr = quoter.quote_parr(PunctuationNotRecognized)

    assert quoted_parr != PunctuationNotRecognized


@pytest.fixture
def Apostrophe() -> str:
    return get_file_content("apostrophe.txt")


@patch_QuoterDirector({"Jim O'Connolly"}, {""})
def test_recognize_name_with_apostrophe(Apostrophe: str):
    quoter = Quoter("", "")

    with mock_ask_confirmation(True) as mock_input:
        quoted_parr = quoter.quote_parr(Apostrophe)
        assert is_to_be_asked("O'Connolly", mock_input)

    assert "Jim O'Connolly" in quoter.quoted_directors
    assert quoted_parr != Apostrophe


@pytest.fixture
def Bunuel() -> str:
    return get_file_content("name_at_first.txt")


@patch_QuoterDirector({"Luis Buñuel"}, {""})
def test_parragraph_starts_with_not_complete_name(Bunuel: str):
    quoter = Quoter("", "")

    with mock_ask_confirmation(True) as mock_input:
        quoted_parr = quoter.quote_parr(Bunuel)
        assert is_to_be_asked("Buñuel", mock_input)

    assert "Luis Buñuel" in quoter.quoted_directors
    assert quoted_parr != Bunuel


@pytest.fixture
def DeLaIglesia() -> str:
    return get_file_content("upper_case_sentence.txt")


@patch_QuoterDirector({"Álex de la Iglesia"}, {""})
def test_lower_name_starts_upper(DeLaIglesia: str):
    quoter = Quoter("", "")

    with mock_ask_confirmation(True) as mock_input:
        quoted_parr = quoter.quote_parr(DeLaIglesia)
        assert is_to_be_asked("De la Iglesia", mock_input)

    assert "Álex de la Iglesia" in quoter.quoted_directors
    assert quoted_parr != DeLaIglesia


@pytest.fixture
def DeHecho() -> str:
    return get_file_content("end_assian.txt")


@patch_QuoterDirector({"Bong Joon-ho"}, {""})
def test_quote_shorter_than_word(DeHecho: str):
    quoter = Quoter("", "")

    with mock_ask_confirmation(False) as mock_input:
        quoted_parr = quoter.quote_parr(DeHecho)
        assert mock_input.call_count == 0

    assert not quoter.quoted_directors
    assert quoted_parr == DeHecho
