from bs4 import BeautifulSoup

from src.aux_console import clear_current_line, go_to_upper_row
from src.blog_scraper import BlogScraper
from src.config import Config, Param, Section
from src.content_mgr import ContentMgr
from src.google_api import Post, Poster, join
from src.list_title_mgr import TitleMgr
from src.make_html import html
from src.pelicula import Pelicula
from src.progress_bar import ProgressBar
from src.read_blog import BlogHiddenData
from src.searcher import Searcher
from src.update_blog.dlg_update_post import DlgUpdatePost
from src.word_reader import WordReader


class BlogThemeUpdater():

    def __init__(self):
        self.Documento = html()
        self.title_manager = TitleMgr(WordReader.list_titles())
        self.all_posts = Poster.get_all_posts()
        self.parsed: BeautifulSoup = None

        # Compruebo que no haya posts repetidos
        self.exist_repeated_posts(self.all_posts)

    def get_word_name_from_blog_post(self, post: Post, *, keep_parsed: bool = False) -> str:
        # Obtengo el nombre a partir del post usando la clase específica
        name, self.parsed = BlogScraper.get_name_and_parsed_from_post(post)

        # Si no me interesa quedarme el post parseado, lo borro
        if not keep_parsed:
            self.parsed = None

        # Devuelvo el nombre que he leído del post
        return name

    def select_and_update_post(self):

        # Creo un diccionario que asocia cada post con su nombre en el word
        word_names = {self.get_word_name_from_blog_post(post): post
                      for post in self.all_posts}

        # Pregunto al usuario cuál quiere actualizar
        dlg = DlgUpdatePost(list(word_names.keys()))
        to_update = dlg.get_ans()

        self.update_post(word_names[to_update])

    def update_post(self, post: Post, *,
                    download_data: bool = Config.get_bool(
                        Section.POST, Param.GET_DATA_FROM_FA),
                    fa_url_from_hidden_data: bool = Config.get_bool(
                        Section.POST, Param.FA_URL_FROM_HIDDEN_DATA)) -> bool:

        # A partir del post busco cuál es su nombre en el Word
        title = self.get_word_name_from_blog_post(post, keep_parsed=True)
        # Si no encuentro su nombre en el Word, salgo
        if not title:
            return False

        if not self.parsed:
            # Parseo el contenido
            self.parsed = BeautifulSoup(post.content, 'lxml')

        # Obtengo la url de la película
        if fa_url_from_hidden_data:
            # Obtengo la dirección desde los datos ocultos de la reseña
            url_fa = BlogHiddenData.URL_FA.get(self.parsed)
        else:
            # No quiero la url que tiene anotada el html.
            # Hago una búsqueda del título en FilmAffinity
            if not (url_fa := Searcher(title).get_url()):
                # Si no encuentro la url, la pido al usuario
                url_fa = input(f"Necesito url de FilmAffinity de {title}. ")

        # Creo un objeto a partir de la url de FA
        self.Documento.data = Pelicula.from_fa_url(url_fa)
        # Normalmente tengo todos los datos necesarios dentro del html.
        # Si me faltara alguno, indico que hay que descargar la página de FA
        if download_data:
            try:
                download_film_data(self.Documento.data)
            except ValueError:
                return False
        else:
            parse_film_data(self.Documento.data, self.parsed)

        # Restituyo el nombre que tenía en Word
        self.Documento.data.titulo = title

        # Escribo el archivo html
        self.Documento.write_html()
        # Extraigo el texto del documento html
        # El resto de datos del post deben quedar intactos
        post_info = ContentMgr.extract_html(self.Documento.sz_file_name)
        post.content = post_info.content
        # Subo el nuevo post
        Poster.update_post(post)

        # Elimino el archivo html que acabo de generar
        self.Documento.delete_file()
        # Limpio el objeto para poder escribir otro html
        self.Documento.reset()
        self.parsed = None

        return True

    def exist_repeated_posts(self, posts: list[Post]) -> bool:

        # Genero un contenedor para guardar los títulos ya visitados
        titles: set[str] = set()

        # Itero todos los posts
        for post in posts:
            # A partir del post busco cuál es su nombre en el Word
            title = self.get_word_name_from_blog_post(post)

            # Compruebo si el título ya lo hemos encontrado antes
            if title in titles:
                print(f"La reseña de {title} está repetida")
            titles.add(title)

        # Devuelvo si hay más posts que títulos
        return len(titles) < len(posts)

    def update_blog(self):

        bar = ProgressBar()
        total_elements = len(self.all_posts)

        for index, post in enumerate(self.all_posts):

            # Imprimo el nombre de la película actual
            clear_current_line()
            print(f"Actualizando {post.title}")

            if not self.update_post(post):
                print(f"Error con la película {post.title}")

            # Imprimo el progreso de la barra
            bar.update((index + 1)/total_elements)
            # Subo a la linea anterior a la barra de progreso
            go_to_upper_row()

        join()


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
