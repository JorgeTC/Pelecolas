from bs4 import BeautifulSoup

from src.aux_console import go_to_upper_row, clear_current_line
from src.content_mgr import ContentMgr
from src.dlg_scroll_base import DlgScrollBase
from src.list_title_mgr import TitleMgr
from src.make_html import html
from src.pelicula import Pelicula
from src.poster import POSTER
from src.progress_bar import ProgressBar
from src.read_blog import BlogHiddenData, ReadBlog
from src.searcher import Searcher


class BlogThemeUpdater():

    def __init__(self, path):
        self.Documento = html(path)
        self.title_manager = TitleMgr(self.Documento.titulos.keys())
        self.content_mgr = ContentMgr(path)
        self.all_posts = POSTER.get_all_posts()
        self.parsed = None

        # Compruebo que no haya posts repetidos
        self.exist_repeated_posts(self.all_posts)

    def get_word_name_from_blog_post(self, post):
        name = post['title']
        # Si el nombre que tiene en el word no es el normal, es que tiene un año
        if self.title_manager.is_title_in_list(name):
            return self.title_manager.exact_key_without_dlg(name)

        # Parseo el contenido
        self.parsed = BeautifulSoup(post['content'], 'html.parser')

        year = self.get_secret_data(BlogHiddenData.YEAR)
        name = f'{name} ({year})'

        if self.title_manager.is_title_in_list(name):
            return self.title_manager.exact_key_without_dlg(name)

        return ""

    def get_secret_data(self, data_id):

        if not self.parsed:
            return None

        return ReadBlog.get_secret_data_from_content(
            self.parsed, data_id)

    def select_and_update_post(self):

        word_names = {}

        # Creo un diccionario que asocia cada post con su nombre en el word
        for post in self.all_posts:
            word_names[self.get_word_name_from_blog_post(post)] = post

        # Pregunto al usuario cuál quiere actualizar
        dlg = DlgScrollBase(question="Elija una reseña para actualizar: ",
                            options=list(word_names.keys()))
        to_update = dlg.get_ans()

        self.update_post(word_names[to_update])

    def update_post(self, post):

        # A partir del post busco cuál es su nombre en el Word
        title = self.get_word_name_from_blog_post(post)
        # Si no encuentro su nombre en el Word, salgo
        if not title:
            return False

        if not self.parsed:
            # Parseo el contenido
            self.parsed = BeautifulSoup(post['content'], 'html.parser')

        # En base al nombre busco su ficha en FA
        url_fa = self.get_secret_data(BlogHiddenData.URL_FA)

        # Cargo los datos de la película de FA
        self.Documento.data = Pelicula.from_fa_url(url_fa)
        self.Documento.data.get_parsed_page()
        # Si no he conseguido leer nada de FA, salgo de la función
        if not self.Documento.data.exists():
            return False
        # Restituyo el nombre que tenía en Word
        self.Documento.data.titulo = title
        # Leo en las notas ocultas del html los datos
        self.Documento.data.director = self.get_secret_data(BlogHiddenData.DIRECTOR)
        self.Documento.data.año = self.get_secret_data(BlogHiddenData.YEAR)
        self.Documento.data.duracion = self.get_secret_data(BlogHiddenData.DURATION)
        self.Documento.data.pais = self.get_secret_data(BlogHiddenData.COUNTRY)
        self.Documento.data.url_image = self.get_secret_data(BlogHiddenData.IMAGE)

        # Escribo el archivo html
        self.Documento.write_html()
        # Extraigo el texto del documento html
        # El resto de datos del post deben quedar intactos
        post_info = self.content_mgr.extract_html(self.Documento.sz_file_name)
        post['content'] = post_info['content']
        # Subo el nuevo post
        POSTER.update_post(post)

        # Elimino el archivo html que acabo de generar
        self.Documento.delete_file()
        # Limpio el objeto para poder escribir otro html
        self.Documento.reset()
        self.parsed = None

        return True

    def exist_repeated_posts(self, posts: list[dict]) -> bool:

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
            print(f"Actualizando {post['title']}")

            if not self.update_post(post):
                print(f"Error con la película {post['title']}")

            # Imprimo el progreso de la barra
            bar.update((index + 1)/total_elements)
            # Subo a la linea anterior a la barra de progreso
            go_to_upper_row()
