import requests

from src.essays.update_blog.blog_theme_updater import update_image_url
from src.pelicula import Pelicula


def test_update_image_url():

    pacifiction = Pelicula.from_id(361131)
    old_image_url = 'https://pics.filmaffinity.com/pacifiction-364246203-mmed.jpg'
    pacifiction.url_image = old_image_url

    # El link no existe
    assert not requests.get(pacifiction.url_image).ok

    update_image_url(pacifiction)

    # El link existe
    assert requests.get(pacifiction.url_image).ok


def test_not_update_image_url():

    ostatni_etap = Pelicula.from_id(423108)
    current_image_url = 'https://pics.filmaffinity.com/ostatni_etap_the_last_stage-370732047-mmed.jpg'
    ostatni_etap.url_image = current_image_url

    # El link existe
    assert requests.get(ostatni_etap.url_image).ok

    update_image_url(ostatni_etap)
    # El link no se ha modificado
    assert ostatni_etap.url_image == current_image_url
    # La página no ha sido parseada
    assert ostatni_etap.film_page is None
