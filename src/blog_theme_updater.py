from bs4 import BeautifulSoup

from src.google_api.api_dataclasses import Post
from src.aux_console import clear_current_line, go_to_upper_row
from src.blog_scraper import BlogScraper
from src.config import Config, Param, Section
from src.content_mgr import ContentMgr
from src.dlg_scroll_base import DlgScrollBase
from src.list_title_mgr import TitleMgr
from src.make_html import html
from src.pelicula import Pelicula
from src.google_api.poster import Poster
from src.progress_bar import ProgressBar
from src.read_blog import BlogHiddenData
from src.searcher import Searcher
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
                    dowload_data: bool = Config.get_bool(
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
        if dowload_data:
            self.Documento.data.get_parsed_page()
            # Si no he conseguido leer nada de FA, salgo de la función
            if not self.Documento.data.exists():
                return False

            # Obtengo los datos de la página de FA
            self.Documento.data.get_director()
            self.Documento.data.get_año()
            self.Documento.data.get_duracion()
            self.Documento.data.get_country()
            self.Documento.data.get_image_url()
        else:
            # Por el contrario leo en las notas ocultas del html los datos
            self.Documento.data.director = BlogHiddenData.DIRECTOR.get(
                self.parsed)
            self.Documento.data.año = BlogHiddenData.YEAR.get(
                self.parsed)
            self.Documento.data.duracion = BlogHiddenData.DURATION.get(
                self.parsed)
            self.Documento.data.pais = BlogHiddenData.COUNTRY.get(
                self.parsed)
            self.Documento.data.url_image = BlogHiddenData.IMAGE.get(
                self.parsed)

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


class DlgUpdatePost(DlgScrollBase):

    def __init__(self, title_list: list[str]):
        DlgScrollBase.__init__(self,
                               question="Elija una reseña para actualizar: ",
                               options=title_list)

        self.quisiste_decir = TitleMgr(title_list)

    def get_ans_body(self) -> str:
        ans = ""
        # Función sobreescrita de la clase base
        while not ans:
            # Inicializo las variables antes de llamar a input
            self.curr_index = -1
            self.sz_options = self.quisiste_decir.get_suggestions()
            self.n_options = len(self.sz_options)
            # Al llamar a input es cuando me espero que se utilicen las flechas
            ans = input(self.sz_question)
            # Se ha introducido un título, compruebo que sea correcto
            ans = self.quisiste_decir.exact_key(ans)

        return ans
