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
