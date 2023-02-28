from unittest import mock
from contextlib import contextmanager
from pathlib import Path
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


def test_essay_name_changed():
    res_folder = get_test_res_folder("word", "name_changed")
    old_name_folder = res_folder / "old_name"
    # Establezco los valores necesarios para escribir el html que nos interesa
    with mock.patch.object(WordFolderMgr, "SZ_ALL_DOCX", get_files(old_name_folder)):
        WordReader.TITULOS = {}
        WordReader.YEARS_PARR = {}
        WordReader.PARAGRAPHS = []
        init_paragraphs(WordReader.YEARS_PARR, WordReader.PARAGRAPHS)
        init_titles(WordReader.HEADER, WordReader.PARAGRAPHS,
                    WordReader.TITULOS)
    old_name = "Érase una vez… en Hollywood"
    assert (old_name in WordReader.TITULOS)

    # Escribo el html de una película que tenga cita en el primer párrafo
    old_name_film = Pelicula()
    old_name_film.titulo = old_name
    old_name_film.id = 169177
    writer = Html(old_name_film)
    add_post_link_path = 'src.essays.html.quoter.quoter_title.add_post_link'
    with mock.patch(add_post_link_path, side_effect=add_post_link) as quote_title:
        writer.write_html()
        # Compruebo que se haya añadido la cita
        assert quote_title.called

    # Compruebo que el archivo exista
    assert (writer.HTML_OUTPUT_FOLDER / writer.sz_file_name).is_file()

    # Actualizo el objeto WordReader
    new_name_folder = res_folder / "new_name"
    with mock.patch.object(WordFolderMgr, "SZ_ALL_DOCX", get_files(new_name_folder)):
        WordReader.TITULOS = {}
        WordReader.YEARS_PARR = {}
        WordReader.PARAGRAPHS = []
        init_paragraphs(WordReader.YEARS_PARR, WordReader.PARAGRAPHS)
        init_titles(WordReader.HEADER, WordReader.PARAGRAPHS,
                    WordReader.TITULOS)
    new_name = "Érase una vez en… Hollywood"
    assert (new_name in WordReader.TITULOS)
    assert (old_name not in WordReader.TITULOS)
    # Si los nombres fueran iguales, no estaría testeando nada
    assert old_name != new_name

    essay = ContentMgr.extract_html(writer.sz_file_name)

    # Actualizo la lista de títulos
    with mock.patch.object(BlogScraper, 'TITLE_MGR', TitleMgr(WordReader.TITULOS.keys())):
        assert len(BlogScraper.TITLE_MGR.TITLES) == 1
        add_post_link_path = 'src.essays.blog_scraper.find_title_by_content'
        with mock.patch(add_post_link_path, side_effect=find_title_by_content) as title_by_content:
            # Compruebo que el nombre sea el nuevo
            assert new_name == BlogScraper.get_name_from_post(essay)
            assert title_by_content.called
