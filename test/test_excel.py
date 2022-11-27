from unittest import mock

from src.excel.utils import is_valid
from src.pelicula import Pelicula


@mock.patch.object(is_valid, "__kwdefaults__", {'SET_VALID_FILM': 1})
def test_valid_film():
    pulp_fiction = Pelicula.from_id(160882)
    assert is_valid(pulp_fiction)


@mock.patch.object(is_valid, "__kwdefaults__", {'SET_VALID_FILM': 1})
def test_not_valid_film():

    thriller = Pelicula.from_id(571895)
    assert not is_valid(thriller)

    luxo = Pelicula.from_id(231149)
    assert not is_valid(luxo)

    cabina = Pelicula.from_id(762673)
    assert not is_valid(cabina)

    simpsons = Pelicula.from_id(372160)
    assert not is_valid(simpsons)

    isabel = Pelicula.from_id(593820)
    assert not is_valid(isabel)
