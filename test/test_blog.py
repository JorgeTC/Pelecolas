import filecmp
import os
import test.mocks_non_substitution as mocks_ns
import test.mocks_word_folder as mocks_w
from contextlib import contextmanager
from datetime import datetime
from unittest import mock

import pytest

from src.aux_res_directory import get_test_res_folder
from src.config import Param, Section
from src.essays.aux_title_str import date_from_YMD
from src.essays.blog_scraper import BlogScraper, find_title_by_content
from src.essays.google_api import Poster
from src.essays.html import Html
from src.essays.html.content_mgr import ContentMgr
from src.essays.html.make_html import ask_for_data
from src.essays.html.quoter import QuoterDirector
from src.essays.html.quoter.quoter_title import add_post_link
from src.essays.list_title_mgr import TitleMgr
from src.essays.update_blog.blog_theme_updater import update_image_url
from src.essays.word.word_reader import WordReader
from src.pelicula import Pelicula
from src.safe_url import safe_response


def test_update_image_url():

    pacifiction = Pelicula.from_id(361131)
    old_image_url = 'https://pics.filmaffinity.com/pacifiction-364246203-mmed.jpg'
    pacifiction.url_image = old_image_url

    # El link no existe
    assert not safe_response(pacifiction.url_image).ok

    update_image_url(pacifiction)

    # El link existe
    assert safe_response(pacifiction.url_image).ok


def test_not_update_image_url():

    ostatni_etap = Pelicula.from_id(423108)
    current_image_url = 'https://pics.filmaffinity.com/ostatni_etap_the_last_stage-370732047-mmed.jpg'
    ostatni_etap.url_image = current_image_url

    # El link existe
    assert safe_response(ostatni_etap.url_image).ok

    update_image_url(ostatni_etap)
    # El link no se ha modificado
    assert ostatni_etap.url_image == current_image_url
    # La página no ha sido parseada
    assert ostatni_etap.film_page is None


@mock.patch.object(QuoterDirector, "TRUST_DIRECTORS", {"Tarantino"})
def test_essay_name_changed():
    res_folder = get_test_res_folder("word", "name_changed")
    old_name_folder = res_folder / "old_name"
    # Establezco los valores necesarios para escribir el html que nos interesa
    with mocks_w.set_word_folder(old_name_folder):
        old_name = "Érase una vez… en Hollywood"
        assert (old_name in WordReader.TITULOS)

        # Escribo el html de una película que tenga cita en el primer párrafo
        old_name_film = Pelicula()
        old_name_film.titulo = old_name
        old_name_film.id = 169177
        writer = Html(old_name_film)
        with mocks_ns.mock_without_replace(add_post_link) as quote_title:
            writer.write_html()
            # Compruebo que se haya añadido la cita
            assert quote_title.called

    # Compruebo que el archivo exista
    assert (writer.HTML_OUTPUT_FOLDER / writer.file_name).is_file()

    # Actualizo el objeto WordReader
    new_name_folder = res_folder / "new_name"
    with mocks_w.set_word_folder(new_name_folder):
        new_name = "Érase una vez en… Hollywood"
        assert (new_name in WordReader.TITULOS)
        assert (old_name not in WordReader.TITULOS)
        # Si los nombres fueran iguales, no estaría testeando nada
        assert old_name != new_name

        essay = ContentMgr.extract_html(writer.file_name)

        # Actualizo la lista de títulos
        with mock.patch.object(BlogScraper, 'TITLE_MGR', TitleMgr(WordReader.TITULOS.keys())):
            assert len(BlogScraper.TITLE_MGR.titles) == 1
            with mocks_ns.mock_without_replace(find_title_by_content) as title_by_content:
                # Compruebo que el nombre sea el nuevo
                assert new_name == BlogScraper.get_name_from_post(essay)
                assert title_by_content.called


@pytest.fixture
def signals() -> Pelicula:
    film_signals = Pelicula.from_id(490014)
    film_signals.titulo = 'Señales'
    film_signals.director = 'M. Night Shyamalan'
    film_signals.año = 2002
    film_signals.duracion = 106
    film_signals.pais = 'Estados Unidos'
    film_signals.url_image = 'https://pics.filmaffinity.com/signs-888503123-large.jpg'
    return film_signals


@mock.patch.object(Html, "HTML_OUTPUT_FOLDER", get_test_res_folder("dump"))
def test_make_html(signals):
    document = Html()
    with mock.patch(mocks_ns.import_path(ask_for_data), return_value=signals):
        document.write_html()
    created_file = document.HTML_OUTPUT_FOLDER / document.file_name
    assert created_file.is_file()
    reference_file = get_test_res_folder('html', 'Reseña Señales.html')
    assert reference_file.is_file()
    assert filecmp.cmp(created_file, reference_file)
    os.remove(created_file)


def delete_last_draft():
    if not (draft_posts := Poster.get_draft_from_date(datetime.today())):
        raise FileNotFoundError
    draft_posts.sort(key=lambda post: date_from_YMD(post.published))
    last_post = draft_posts[-1]
    Poster.delete_post(last_post)


@contextmanager
def temp_draft_post():
    try:
        # Hago la publicación en borrador y cojo fecha automática
        with (mocks_ns.mock_config_get_bool(Section.POST, Param.AS_DRAFT, True),
              mocks_ns.mock_config_get_value(Section.POST, Param.DATE, 'auto')):
            yield None
    finally:
        delete_last_draft()


@mock.patch.object(Html, "HTML_OUTPUT_FOLDER", get_test_res_folder("dump"))
@mock.patch.object(ContentMgr, "DIR", get_test_res_folder("dump"))
def test_post_html():
    reference_file = get_test_res_folder('html', 'Reseña Señales.html')
    assert reference_file.is_file()

    # Leo el html escrito y extraigo los datos necesarios para hacer la publicación
    post_data = ContentMgr.extract_html(reference_file)

    with temp_draft_post():
        Poster.add_post(title=post_data.title,
                        content=post_data.content,
                        labels=post_data.labels)
