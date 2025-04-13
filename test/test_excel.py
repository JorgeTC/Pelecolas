from src.pelicula import FAType, Pelicula
from src.scrap_fa.excel.utils import FilmValid, is_valid


def test_valid_film():

    valid_filter = FilmValid.FILM

    pulp_fiction = Pelicula.from_id(160882)
    assert is_valid(pulp_fiction, valid_filter)


def test_not_valid_film():

    valid_filter = FilmValid.FILM

    thriller = Pelicula.from_id(571895)
    assert not is_valid(thriller, valid_filter)

    luxo = Pelicula.from_id(231149)
    assert not is_valid(luxo, valid_filter)

    cabina = Pelicula.from_id(762673)
    assert not is_valid(cabina, valid_filter)

    simpsons = Pelicula.from_id(372160)
    assert not is_valid(simpsons, valid_filter)

    isabel = Pelicula.from_id(593820)
    assert not is_valid(isabel, valid_filter)


def test_multiple_is_valid():

    # Es un videoclip y además de animación
    take_on_me = Pelicula.from_id(852164)
    # Como no aceptamos videoclip, no debe ser válido
    assert not is_valid(take_on_me, FilmValid.FILM | FilmValid.ANIMATION)
    assert not is_valid(take_on_me, FilmValid.ANIMATION)
    assert not is_valid(take_on_me, FilmValid.FILM | FilmValid.MUSIC_VIDEO)
    assert not is_valid(take_on_me, FilmValid.MUSIC_VIDEO)
    assert is_valid(take_on_me, FilmValid.ANIMATION | FilmValid.MUSIC_VIDEO)
    # Comprobar que los tags son los que esperábamos
    assert take_on_me.FA_type == {FAType.ANIMATION, FAType.MUSIC_VIDEO}
