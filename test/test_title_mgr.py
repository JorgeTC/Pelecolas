import pytest

from src.essays.list_title_mgr import TitleMgr


@pytest.fixture
def quisiste_decir() -> TitleMgr:
    return TitleMgr(["Cantando bajo la lluvia",
                     "Él",
                     "La caza (1966)",
                     "El Topo",
                     "La caza (2020)",
                     "El último",
                     "Peppermint Frappé",
                     "El gabinete del Dr. Caligari"])


def test_exact_key(quisiste_decir: TitleMgr):
    title = "Cantando bajo la lluvia"
    assert quisiste_decir.exact_key(title) == title


def test_not_print_when_exact_key(quisiste_decir: TitleMgr):
    title = "Cantando bajo la lluvia"
    exact_key = quisiste_decir.exact_key(title)
    assert exact_key == title


def test_exact_but_case(quisiste_decir: TitleMgr):
    title = "El topo"
    exact_key = quisiste_decir.exact_key(title)
    # Compruebo que haya modificado el título
    assert exact_key != title
    # Pero que sea el mismo título introducido
    assert exact_key.lower() == title.lower()


def test_not_suggestions(quisiste_decir: TitleMgr):
    title = "(1312)"
    assert quisiste_decir.exact_key(title) == ""


def test_exact_but_accent(quisiste_decir: TitleMgr):
    title = "El ultimo"
    # No me espero que corrija el acento
    assert quisiste_decir.exact_key(title) == ""
    # Pero me espero que se encuentre entre los títulos sugeridos
    assert "El último" in quisiste_decir.suggestions(title)


def test_exact_but_spaces(quisiste_decir: TitleMgr):
    title = "  Cantando   bajo la lluvia "
    assert not quisiste_decir.exists(title)
    # Compruebo que haya sido capaz de encontrar coincidencia
    assert "Cantando bajo la lluvia" in quisiste_decir.suggestions(title)


def test_exact_but_double_letters(quisiste_decir: TitleMgr):
    title = "Pepermint frape"
    assert not quisiste_decir.exists(title)
    # Compruebo que haya sido capaz de encontrar coincidencia
    assert "Peppermint Frappé" in quisiste_decir.suggestions(title)


def test_partial_title(quisiste_decir: TitleMgr):
    title = "lluvia"
    assert not quisiste_decir.exists(title)
    # Compruebo que haya sido capaz de encontrar coincidencia
    assert "Cantando bajo la lluvia" in quisiste_decir.suggestions(title)


def test_title_with_year(quisiste_decir: TitleMgr):
    title = "Cantando bajo la lluvia (1952)"
    assert not quisiste_decir.exists(title)
    # Compruebo que haya sido capaz de encontrar coincidencia
    assert "Cantando bajo la lluvia" in quisiste_decir.suggestions(title)


'''
def test_doctor(quisiste_decir: TitleMgr):
    title = "El gabinete del doctor Caligari"
    assert not quisiste_decir.exists(title)
    assert "El gabinete del Dr. Caligari" in quisiste_decir.suggestions(title)
'''
