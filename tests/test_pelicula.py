import pytest
from src.pelicula import Pelicula, read_avg_note_from_page


@pytest.fixture
def film() -> Pelicula:
    pulp_fiction = Pelicula.from_id(160882)
    pulp_fiction.get_parsed_page()
    return pulp_fiction


@pytest.fixture
def film_without_length() -> Pelicula:
    maxcotas = Pelicula.from_fa_url(
        'https://www.filmaffinity.com/es/film309052.html')
    maxcotas.get_parsed_page()
    return maxcotas


@pytest.fixture
def film_without_note() -> Pelicula:
    vuelve_a_casa = Pelicula.from_id(148859)
    vuelve_a_casa.get_parsed_page()
    return vuelve_a_casa


def test_wrong_id():
    wrong_film = Pelicula.from_id(7)
    with pytest.raises(AttributeError):
        wrong_film.get_title()
    assert wrong_film.exists() == False


def test_scrap_title():
    jaws = Pelicula.from_id(242422)
    jaws.get_title()
    assert jaws.titulo == 'Tiburón '


def test_scrap_country(film: Pelicula):
    film.get_country()
    assert film.pais == 'Estados Unidos'


def test_scrap_year(film: Pelicula):
    film.get_año()
    assert isinstance(film.año, str)
    assert film.año == '1994'


def test_scrap_director(film: Pelicula):
    film.get_director()
    assert film.director == 'Quentin Tarantino'


def test_scrap_image(film: Pelicula):
    film.get_image_url()
    assert film.url_image == 'https://pics.filmaffinity.com/pulp_fiction-210382116-mmed.jpg'


def test_not_rescrap_know_data():
    film = Pelicula.from_id(160882)
    film.director = 'Wrong director'
    film.get_director()
    assert film.director == 'Wrong director'
    assert film.parsed_page is None


def test_scrap_note(film: Pelicula):
    film.get_nota_FA()
    note_in_page = read_avg_note_from_page(film.parsed_page)
    assert film.nota_FA == pytest.approx(note_in_page, 0.1)


def test_scrap_votes(film: Pelicula):
    film.get_votantes_FA()
    assert film.votantes_FA > 1_000


def test_scrap_without_note(film_without_note: Pelicula):

    film_without_note.get_nota_FA()

    # Compruebo que la página no tenga en efecto nota media
    assert read_avg_note_from_page(film_without_note.parsed_page) == 0

    assert film_without_note.nota_FA == 0

    film_without_note.get_votantes_FA()
    assert film_without_note.votantes_FA == 0


def test_scrap_desvest(film: Pelicula):
    film.get_desvest()
    assert film.desvest_FA > 0


def test_scrap_desvest_without_note(film_without_note: Pelicula):
    film_without_note.get_desvest()
    assert film_without_note.desvest_FA == 0


def test_scrap_duration(film: Pelicula):
    film.get_duracion()
    assert film.duracion == 153


def test_scrap_without_duration(film_without_length: Pelicula):
    film_without_length.get_duracion()
    assert film_without_length.duracion == 0

    film_without_length.parsed_page = None
    film_without_length.get_duracion()
    assert film_without_length.parsed_page is None


def test_scrap_prop_aprobados(film: Pelicula):
    film.get_prop_aprobados()
    assert 0.5 < film.prop_aprobados < 1


def test_scrap_prop_aprobados_without_note(film_without_note: Pelicula):
    film_without_note.get_prop_aprobados()
    assert film_without_note.prop_aprobados == 0


def test_valid_film(film: Pelicula):
    assert film.valid()


def test_not_valid_film():

    thriller = Pelicula.from_id(571895)
    assert not thriller.valid()

    luxo = Pelicula.from_id(231149)
    assert not luxo.valid()

    cabina = Pelicula.from_id(762673)
    assert not cabina.valid()

    simpsons = Pelicula.from_id(372160)
    assert not simpsons.valid()

    isabel = Pelicula.from_id(593820)
    assert not isabel.valid()
