from threading import Thread, current_thread

import src.google_api as GoogleApi
import src.gui as GUI
from bs4 import BeautifulSoup
from src.blog_scraper import BlogScraper
from src.config import Config, Param, Section
from src.content_mgr import ContentMgr
from src.google_api import Post, Poster
from src.make_html import html
from src.pelicula import Pelicula
from src.read_blog import BlogHiddenData
from src.searcher import Searcher
from src.update_blog.dlg_update_post import DlgUpdatePost
from src.update_blog.thread_executor import ThreadExecutor


class PostThemeUpdater:

    DOWNLOAD_DATA: bool = Config.get_bool(
        Section.POST, Param.GET_DATA_FROM_FA)

    FA_URL_FROM_HIDDEN_DATA: bool = Config.get_bool(
        Section.POST, Param.FA_URL_FROM_HIDDEN_DATA)

    @classmethod
    def select_post_to_update(self):

        ALL_POSTS = Poster.get_all_posts()

        # Creo un diccionario que asocia cada post con su nombre en el word
        word_names = {BlogScraper.get_name_from_post(post): post
                      for post in ALL_POSTS}

        # Pregunto al usuario cuál quiere actualizar
        dlg = DlgUpdatePost(list(word_names.keys()))
        to_update = dlg.get_ans()

        return word_names[to_update]

    @classmethod
    def update_post(cls, post: Post):
        # Parseo el contenido
        parsed = BeautifulSoup(post.content, 'lxml')

        # A partir del post busco cuál es su nombre en el Word
        title = BlogScraper.get_name_from_post(post, parsed)
        # Si no encuentro su nombre en el Word, salgo
        if not title:
            return False

        # Obtengo la url de la película
        if cls.FA_URL_FROM_HIDDEN_DATA:
            # Obtengo la dirección desde los datos ocultos de la reseña
            url_fa = BlogHiddenData.URL_FA.get(parsed)
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
            parse_film_data(film_data, parsed)

        # Restituyo el nombre que tenía en Word
        film_data.titulo = title

        # Escribo el archivo html
        document = html(film_data)
        document.write_html()
        # Extraigo el texto del documento html
        # El resto de datos del post deben quedar intactos
        post_info = ContentMgr.extract_html(document.sz_file_name)
        post.content = post_info.content
        # Subo el nuevo post
        Poster.update_post(post)

        return True


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


def parse_film_data(film: Pelicula, blog_page: BeautifulSoup):
    # Leo en las notas ocultas del html los datos
    film.director = BlogHiddenData.DIRECTOR.get(blog_page)
    film.año = BlogHiddenData.YEAR.get(blog_page)
    film.duracion = BlogHiddenData.DURATION.get(blog_page)
    film.pais = BlogHiddenData.COUNTRY.get(blog_page)
    film.url_image = BlogHiddenData.IMAGE.get(blog_page)
