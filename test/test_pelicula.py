import pytest

from src.pelicula import Pelicula, FAType


@pytest.fixture
def film() -> Pelicula:
    pulp_fiction = Pelicula.from_id(160882)
    pulp_fiction.get_parsed_page()
    return pulp_fiction


@pytest.fixture
def film_without_length() -> Pelicula:
    maxcotas_url = 'https://www.filmaffinity.com/es/film309052.html'
    maxcotas = Pelicula.from_fa_url(maxcotas_url)
    maxcotas.get_parsed_page()
    return maxcotas


@pytest.fixture
def film_without_note() -> Pelicula:
    amazonas = Pelicula.from_id(623077)
    amazonas.get_parsed_page()
    return amazonas


def test_wrong_id():
    wrong_film = Pelicula.from_id(7)
    with pytest.raises(AttributeError):
        wrong_film.get_title()
    assert wrong_film.exists() == False


def test_scrap_title():
    jaws = Pelicula.from_id(242422)
    jaws.get_title()
    assert jaws.titulo == 'Tiburón'


def test_scrap_country(film: Pelicula):
    film.get_country()
    assert film.pais == 'Estados Unidos'


def test_scrap_year(film: Pelicula):
    film.get_año()
    assert isinstance(film.año, int)
    assert film.año == 1994


def test_scrap_director(film: Pelicula):
    assert film.film_page.is_desktop_version() == True
    film.get_director()
    assert film.director == 'Quentin Tarantino'

def test_scrap_director_mobile():
    # Crear el objeto Pelicula a partir de una URL móvil
    url_mobile = 'https://m.filmaffinity.com/es/film160882.html'
    film_mobile = Pelicula.from_fa_url(url_mobile)
    film_mobile.get_parsed_page()
    # Compruebo que sea versión móvil
    assert film_mobile.film_page.is_desktop_version() == False
    film_mobile.get_director()
    assert film_mobile.director == 'Quentin Tarantino'


def test_several_directors():
    hermano_oso = Pelicula.from_id(321572)
    hermano_oso.get_director()
    assert hermano_oso.director == 'Aaron Blaise'
    assert hermano_oso.directors == ['Aaron Blaise', 'Bob Walker']


def test_no_director():
    madre_de_jose = Pelicula.from_id(306645)
    madre_de_jose.get_director()
    assert madre_de_jose.director == ''
    assert madre_de_jose.directors is not None
    assert madre_de_jose.directors == []


def test_director_with_parenthesis():
    big_bang = Pelicula.from_id(234364)
    big_bang.get_director()
    # En FA el nombre aparece con la apostilla '(Creador)',
    # no quiero que eso se añada a la clase
    assert big_bang.director == 'Chuck Lorre'
    # Algunos directores están escondidos, pero debe poder leerlos igualmente
    assert len(big_bang.directors) == 13


def test_scrap_image(film: Pelicula):
    film.get_image_url()
    assert film.url_image == 'https://pics.filmaffinity.com/pulp_fiction-210382116-mmed.jpg'


def test_not_rescrap_know_data():
    film = Pelicula.from_id(160882)
    film.director = 'Wrong director'
    film.get_director()
    assert film.director == 'Wrong director'
    assert film.film_page is None


def test_scrap_note(film: Pelicula):
    film.get_nota_FA()
    note_in_page = film.film_page.get_avg_note()
    assert film.nota_FA == pytest.approx(note_in_page, 0.1)


def test_scrap_votes(film: Pelicula):
    film.get_votantes_FA()
    assert film.votantes_FA > 1_000


def test_scrap_without_note(film_without_note: Pelicula):

    film_without_note.get_nota_FA()

    # Compruebo que la página no tenga en efecto nota media
    assert film_without_note.film_page.get_avg_note() == 0

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

    film_without_length.film_page = None
    film_without_length.get_duracion()
    assert film_without_length.film_page is None


def test_scrap_prop_aprobados(film: Pelicula):
    film.get_prop_aprobados()
    assert 0.5 < film.prop_aprobados < 1


def test_scrap_prop_aprobados_without_note(film_without_note: Pelicula):
    film_without_note.get_prop_aprobados()
    assert film_without_note.prop_aprobados == 0


def test_scrap_types_none(film: Pelicula):
    film.get_FA_type()
    assert film.FA_type == set()


def test_scrap_types():
    take_on_me = Pelicula.from_id(852164)
    take_on_me.get_FA_type()
    assert take_on_me.FA_type == {FAType.ANIMATION, FAType.MUSIC_VIDEO}
