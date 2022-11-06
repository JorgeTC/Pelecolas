from src.aux_title_str import split_title_year, trim_year
from src.blog_csv_mgr import CSV_COLUMN, BlogCsvMgr
from src.config import Config, Param, Section
from src.google_api import Poster
from src.gui import DlgScrollBase, Input
from src.list_title_mgr import TitleMgr
from src.pelicula import Pelicula
from src.searcher import Searcher
from src.url_FA import URL_FILM_ID


class DlgScrollTitles(DlgScrollBase):

    def __init__(self, question: str, title_list: list[str]):
        DlgScrollBase.__init__(self, question)

        # Objeto para buscar si el título que ha pedido el usuario
        # está disponible en el archivo word.
        self.quisiste_decir = TitleMgr(title_list)

    def get_ans_body(self) -> str:
        # Función sobreescrita de la clase base
        while not self.sz_ans:
            # Inicializo las variables antes de llamar a input
            self.curr_index = -1
            self.sz_options = self.quisiste_decir.get_suggestions()
            self.n_options = len(self.sz_options)
            # Al llamar a input es cuando me espero que se utilicen las flechas
            self.sz_ans = input(self.sz_question)
            # Se ha introducido un título, compruebo que sea correcto
            self.sz_ans = self.quisiste_decir.exact_key(self.sz_ans)

        return self.sz_ans


class DlgHtml:

    # Mensajes para pedir información
    ASK_TITLE = "Introduzca título de la película: "
    ASK_DIRECTOR = "Introduzca director: "
    ASK_YEAR = "Introduzca el año: "
    ASK_DURATION = "Introduzca duración de la película: "

    def __init__(self, title_list: list[str]) -> None:
        if Config.get_bool(Section.HTML, Param.FILTER_PUBLISHED):
            title_list = unpublished(title_list)
        self.title_list = title_list

        # Valores que debo devolver para el objeto html
        # titulo, año, director, duración
        # Los guardo todos en un objeto Pelicula
        self.data = Pelicula()

    def ask_for_data(self):
        # Pido los datos de la película que voy a buscar
        # Titulo
        titles_dlg = DlgScrollTitles(self.ASK_TITLE, self.title_list)
        self.data.titulo = titles_dlg.get_ans()

        # Trato de buscar información de esta película en FA.
        FA = Searcher(self.data.titulo)
        FA.print_state()

        while not self.data.director:
            self.data.director = Input(self.ASK_DIRECTOR)
            # Si en vez de un director se introduce la dirección de FA, no necesito nada más
            if not self.__interpretate_director(FA.get_url()):
                return

        self.data.año = Input(self.ASK_YEAR)
        self.data.duracion = Input(self.ASK_DURATION)

    def __interpretate_director(self, suggested_url: str) -> bool:

        # Caso en el que no se ha introducido nada.
        # Busco la ficha automáticamente.
        if not self.data.director:
            if suggested_url and self.__get_data_from_FA(suggested_url):
                # Lo introducido no es un director.
                # Considero que no necesito más información.
                return False

        # Si es un número, considero que se ha introducido un id de Filmaffinitty
        if self.data.director.isnumeric():
            url = URL_FILM_ID(self.data.director)
            return not self.__get_data_from_FA(url)

        if self.data.director.find("filmaffinity") >= 0:
            # Se ha introducido directamente la url
            return not self.__get_data_from_FA(self.data.director)

        else:
            # El director de la película es lo introducido por teclado
            return True

    def __get_data_from_FA(self, url: str) -> bool:
        # No quiero que se modifique el título que tengo leído.
        # El actual lo he obtenido del word,
        # Pelicula me puede dar un título de FA que no sea idéntico al que hay en el word
        ori_title = self.data.titulo

        self.data = Pelicula.from_fa_url(url)
        self.data.get_parsed_page()

        if not self.data.exists():
            return False

        self.data.titulo = ori_title
        self.data.get_director()
        self.data.get_año()
        self.data.get_duracion()
        self.data.get_country()
        self.data.get_image_url()
        return True


def unpublished(ls_titles: list[str]) -> list[str]:
    # Objeto capaz de leer el csv con todos los títulos publicados
    csv = BlogCsvMgr.open_to_read()
    # Pido la lista de posts por publicar
    csv = csv + [BlogCsvMgr.get_csv_row_from_post(post)
                 for post in Poster.get_scheduled()]

    return filter_list_from_csv(ls_titles, csv)


def filter_list_from_csv(titles: list[str], csv: list[list[str]]):
    # Obtengo la lista de títulos,
    # por si están entrecomillados, quito las comillas
    published = (row[0].strip("\"") for row in csv)
    # quito los posibles años entre paréntesis
    published = (trim_year(title) for title in published)
    published = [title.lower() for title in published]
    lower_titles = (title.lower() for title in titles)

    unpublished_titles: list[str] = []
    for title, lower_title in zip(titles, lower_titles):
        # Compruebo que no tenga escrito el año
        candidato_año, lower_title = split_title_year(lower_title)

        if candidato_año:
            # Compruebo que esté el título en la lista de publicados
            indices = all_indices_in_list(published, lower_title)
            # Compruebo que el año sea correcto.
            # Esta comprobación la hacemos para los casos en los que un título
            # se haya añadido al Word sin año y posteriormente se haya añadido el año.
            if not any(candidato_año == csv[ocurr][CSV_COLUMN.YEAR]
                       for ocurr in indices):
                # Añado el título con las mayúsculas originales
                unpublished_titles.append(title)

        # No tiene año
        elif lower_title not in published:
            # Añado el título con las mayúsculas originales
            unpublished_titles.append(title)

    return unpublished_titles


def all_indices_in_list(ls, el) -> list[int]:
    '''
    Dado un elemento, lo busco en una lista.
    Devuelvo las posiciones de la lista que contengan al elemento
    '''
    return [i for i, ltr in enumerate(ls) if ltr == el]
