import inspect
import os
from contextlib import contextmanager
from pathlib import Path
from typing import Callable, Iterator
from unittest import mock

import requests

from src.aux_res_directory import get_test_res_folder
from src.essays.blog_scraper import BlogScraper, find_title_by_content
from src.essays.html import Html
from src.essays.html.content_mgr import ContentMgr
from src.essays.html.quoter.quoter_title import add_post_link
from src.essays.list_title_mgr import TitleMgr
from src.essays.update_blog.blog_theme_updater import update_image_url
from src.essays.word.word_folder_mgr import WordFolderMgr, get_files
from src.essays.word.word_reader import (WordReader, init_paragraphs,
                                         init_titles)
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


@contextmanager
def set_word_folder(word_folder: Path):

    # Guardo los valores que tendré que reestablecer
    original_titles = WordReader.TITULOS
    original_year_parrs = WordReader.YEARS_PARR
    original_paragraphs = WordReader.PARAGRAPHS

    # Escribo los valores con la actual carpeta de Word
    with mock.patch.object(WordFolderMgr, "SZ_ALL_DOCX", get_files(word_folder)):
        WordReader.TITULOS = {}
        WordReader.YEARS_PARR = {}
        WordReader.PARAGRAPHS = []
        init_paragraphs(WordReader.YEARS_PARR, WordReader.PARAGRAPHS)
        init_titles(WordReader.HEADER, WordReader.PARAGRAPHS,
                    WordReader.TITULOS)

    try:
        yield
    finally:
        # Devuelvo el valor original
        WordReader.TITULOS = original_titles
        WordReader.YEARS_PARR = original_year_parrs
        WordReader.PARAGRAPHS = original_paragraphs


@contextmanager
def mock_without_replace(to_mock: Callable) -> Iterator[mock.MagicMock]:

    # Compongo la ruta de importación
    function_path = to_mock.__name__
    definition_path = Path(inspect.getfile(to_mock))
    while definition_path.stem != 'src':
        function_path = definition_path.stem + "." + function_path
        definition_path = definition_path.parent
    function_path = "src." + function_path

    # Devuelvo la función con su implementación
    with mock.patch(function_path, side_effect=to_mock) as function_mock:
        yield function_mock


def test_essay_name_changed():
    res_folder = get_test_res_folder("word", "name_changed")
    old_name_folder = res_folder / "old_name"
    # Establezco los valores necesarios para escribir el html que nos interesa
    with set_word_folder(old_name_folder):
        old_name = "Érase una vez… en Hollywood"
        assert (old_name in WordReader.TITULOS)

        # Escribo el html de una película que tenga cita en el primer párrafo
        old_name_film = Pelicula()
        old_name_film.titulo = old_name
        old_name_film.id = 169177
        writer = Html(old_name_film)
        with mock_without_replace(add_post_link) as quote_title:
            writer.write_html()
            # Compruebo que se haya añadido la cita
            assert quote_title.called

    # Compruebo que el archivo exista
    assert (writer.HTML_OUTPUT_FOLDER / writer.sz_file_name).is_file()

    # Actualizo el objeto WordReader
    new_name_folder = res_folder / "new_name"
    with set_word_folder(new_name_folder):
        new_name = "Érase una vez en… Hollywood"
        assert (new_name in WordReader.TITULOS)
        assert (old_name not in WordReader.TITULOS)
        # Si los nombres fueran iguales, no estaría testeando nada
        assert old_name != new_name

        essay = ContentMgr.extract_html(writer.sz_file_name)

        # Actualizo la lista de títulos
        with mock.patch.object(BlogScraper, 'TITLE_MGR', TitleMgr(WordReader.TITULOS.keys())):
            assert len(BlogScraper.TITLE_MGR.TITLES) == 1
            with mock_without_replace(find_title_by_content) as title_by_content:
                # Compruebo que el nombre sea el nuevo
                assert new_name == BlogScraper.get_name_from_post(essay)
                assert title_by_content.called

@mock.patch.object(Html, "HTML_OUTPUT_FOLDER", get_test_res_folder("dump"))
def test_make_html():
    signals = Pelicula.from_id(490014)
    signals.titulo = 'Señales'
    document = Html()
    with mock.patch('src.essays.html.make_html.ask_for_data', return_value=signals):
        document.write_html()
    assert (document.HTML_OUTPUT_FOLDER / document.sz_file_name).is_file()
    os.remove(document.HTML_OUTPUT_FOLDER / document.sz_file_name)
