from functools import wraps
from multiprocessing.pool import ThreadPool
from queue import Queue
from threading import Thread
from bs4 import BeautifulSoup

from multiprocessing import current_process

from src.blog_scraper import BlogScraper
from src.config import Config, Param, Section
from src.content_mgr import ContentMgr
from src.google_api import Post, Poster
import src.google_api as GoogleApi
from src.make_html import html
from src.pelicula import Pelicula
from src.progress_bar import ProgressBar
from src.read_blog import BlogHiddenData
from src.searcher import Searcher
from src.update_blog.dlg_update_post import DlgUpdatePost
from src.gui.log import Log
from src.gui.input import Input
import src.gui as GUI




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
                url_fa = Input(f"Necesito url de FilmAffinity de {title}. ")

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


def update_and_notify(post: Post):
    current_process().name = post.title

    # Imprimo el nombre de la película actual
    Log(f"Actualizando {post.title}")

    if not PostThemeUpdater.update_post(post):
        Log(f"Error con la película {post.title}")

    GUI.GUI.close_suite()


class ThreadExecutor:
    def __init__(self, threads: list[Thread], max_executors: int = 3) -> None:
        self.q = Queue()

        self.threads = [self.decorate_thread(thread)
                        for thread in threads]

        self.max_executors = max_executors

    def decorate_thread(self, ori_thread: Thread) -> Thread:
        target = ori_thread._target
        target_decorated = self.queue_when_done(target)
        args = ori_thread._args
        kwargs = ori_thread._kwargs
        name = ori_thread._name

        return Thread(name=name,
                      args=args,
                      kwargs=kwargs,
                      target=target_decorated)

    def execute(self):
        max_executors = min(len(self.threads), self.max_executors)
        threads = self.threads

        # Inicializo todos los hilos
        for _ in range(max_executors):
            threads.pop().start()

        while self.q.get() is not None:
            if not threads:
                continue
            # No inicializo otro hilo hasta que se haya terminado otro
            threads.pop().start()
            # Si he acabado los hilos, añado un indicativo de que la Queue se ha acabado
            if not threads:
                self.q.put(None)

        # Espero a que estén todos acabados
        for thread in self.threads:
            thread.join()


    def queue_when_done(self, fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            ans = fn(*args, **kwargs)
            self.q.put(True)
            return ans
        return wrapper


class BlogThemeUpdater:

    @staticmethod
    def update_blog():

        ALL_POSTS = Poster.get_all_posts()

        threads = [Thread(target=update_and_notify, args=(post,), name=post.title)
                   for post in ALL_POSTS]
        ThreadExecutor(threads).execute()

        GUI.join()
        GoogleApi.join()


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
            Log(f"La reseña de {title} está repetida")
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
