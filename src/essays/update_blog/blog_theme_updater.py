from threading import Thread, current_thread

import requests

import src.gui as GUI
from src.config import Config, Param, Section
from src.pelicula import Pelicula

from .. import google_api as GoogleApi
from ..blog_scraper import BlogHiddenData, BlogScraper
from ..dlg_scroll_titles import DlgScrollTitles
from ..google_api import Post, Poster
from ..html import ContentMgr, Html
from ..searcher import Searcher
from .thread_executor import ThreadExecutor


class PostThemeUpdater:

    DOWNLOAD_DATA: bool = Config.get_bool(
        Section.POST, Param.GET_DATA_FROM_FA)

    FA_URL_FROM_HIDDEN_DATA: bool = Config.get_bool(
        Section.POST, Param.FA_URL_FROM_HIDDEN_DATA)

    CHECK_IMAGE_URL: bool = Config.get_bool(
        Section.POST, Param.CHECK_IMAGE_URL)

    @classmethod
    def select_post_to_update(self):

        ALL_POSTS = Poster.get_all_posts()

        # Creo un diccionario que asocia cada post con su nombre en el word
        word_names = {BlogScraper.get_name_from_post(post): post
                      for post in ALL_POSTS}

        # Pregunto al usuario cuál quiere actualizar
        dlg = DlgScrollTitles("Elija una reseña para actualizar: ",
                              list(word_names.keys()))
        to_update = dlg.get_ans()

        return word_names[to_update]

    @classmethod
    def update_post(cls, post: Post):
        # Construyo un objeto para extraer datos del Post
        blog_scraper = BlogScraper(post)

        # A partir del post busco cuál es su nombre en el Word
        title = blog_scraper.get_title()
        # Si no encuentro su nombre en el Word, salgo
        if not title:
            return False

        # Obtengo la url de la película
        if cls.FA_URL_FROM_HIDDEN_DATA:
            # Obtengo la dirección desde los datos ocultos de la reseña
            url_fa = blog_scraper.get_hidden_data(BlogHiddenData.URL_FA)
        else:
            # No quiero la url que tiene anotada el html.
            # Hago una búsqueda del título en FilmAffinity
            if not (url_fa := Searcher(title).get_url()):
                # Si no encuentro la url, la pido al usuario
                url_fa = GUI.Input(
                    f"Necesito url de FilmAffinity de {title}. ")

        # Creo un objeto a partir de la url de FA
        film_data = Pelicula.from_fa_url(url_fa)
        # Normalmente tengo todos los datos necesarios dentro del html.
        # Si me faltara alguno, indico que hay que descargar la página de FA
        if cls.DOWNLOAD_DATA:
            try:
                download_film_data(film_data)
            except ValueError:
                return False
        else:
            parse_film_data(film_data, blog_scraper)
            # Solo tiene sentido que compruebe su url si he cogido el dato del html
            if cls.CHECK_IMAGE_URL:
                update_image_url(film_data)

        # Restituyo el nombre que tenía en Word
        film_data.titulo = title

        # Escribo el archivo html
        document = Html(film_data)
        document.write_html()
        # Extraigo el texto del documento html
        # El resto de datos del post deben quedar intactos
        post_info = ContentMgr.extract_html(document.sz_file_name)
        post.content = post_info.content
        # Subo el nuevo post
        Poster.update_post(post)
        # Elimino el archivo html
        document.delete_file()

        return True


def update_image_url(film_data: Pelicula):
    # Compruebo que la url de la imagen exista
    image_response = requests.get(film_data.url_image)
    if image_response.ok:
        return

    # Si no existe, borro el dato y pido al objeto que lo busque en FA
    film_data.url_image = None
    film_data.get_image_url()


class BlogThemeUpdater:

    def __init__(self) -> None:
        self.progress_bar: GUI.ProgressBar = None

    def update_blog(self):

        ALL_POSTS = Poster.get_all_posts()
        self.progress_bar = GUI.ProgressBar(len(ALL_POSTS))

        threads = [Thread(target=self.update_and_notify, args=(post,), name=post.title)
                   for post in ALL_POSTS]
        ThreadExecutor(threads).execute()

        GUI.join_GUI()
        GoogleApi.join()

    def update_and_notify(self, post: Post):
        current_thread().name = post.title

        # Imprimo el nombre de la película actual
        GUI.Log(f"Actualizando {post.title}")

        if not PostThemeUpdater.update_post(post):
            GUI.Log(f"Error con la película {post.title}")

        self.progress_bar.update()

        GUI.GUI.close_suite()


def exist_repeated_posts() -> bool:

    posts = Poster.get_all_posts()

    # Genero un contenedor para guardar los títulos ya visitados
    titles: set[str] = set()

    # Itero todos los posts
    for post in posts:
        # A partir del post busco cuál es su nombre en el Word
        title = BlogScraper.get_name_from_post(post)

        # Compruebo si el título ya lo hemos encontrado antes
        if title in titles:
            GUI.Log(f"La reseña de {title} está repetida")
        titles.add(title)

    # Devuelvo si hay más posts que títulos
    return len(titles) < len(posts)


def download_film_data(film: Pelicula):
    film.get_parsed_page()
    # Si no he conseguido leer nada de FA, salgo de la función
    if not film.exists():
        raise ValueError

    # Obtengo los datos de la página de FA
    film.get_director()
    film.get_año()
    film.get_duracion()
    film.get_country()
    film.get_image_url()


def parse_film_data(film: Pelicula, blog_scraper: BlogScraper):
    # Leo en las notas ocultas del html los datos
    film.director = blog_scraper.get_hidden_data(BlogHiddenData.DIRECTOR)
    film.año = int(blog_scraper.get_hidden_data(BlogHiddenData.YEAR))
    film.duracion = int(blog_scraper.get_hidden_data(BlogHiddenData.DURATION))
    film.pais = blog_scraper.get_hidden_data(BlogHiddenData.COUNTRY)
    film.url_image = blog_scraper.get_hidden_data(BlogHiddenData.IMAGE)
