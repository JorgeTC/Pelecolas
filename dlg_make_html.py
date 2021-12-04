from blog_csv_mgr import BlogCsvMgr
from dlg_config import CONFIG
from dlg_scroll_base import DlgScrollBase
from list_title_mgr import TitleMgr
from Pelicula import Pelicula
from poster import POSTER
from searcher import Searcher
from url_FA import URL_FILM_ID


class DlgHtml(DlgScrollBase):

    # Mensajes para pedir información
    ASK_TITLE = "Introduzca título de la película: "
    ASK_DIRECTOR = "Introduzca director: "
    ASK_YEAR = "Introduzca el año: "
    ASK_DURATION = "Introduzca duración de la película: "

    def __init__(self, title_list) -> None:
        if CONFIG.get_bool(CONFIG.S_HTML, CONFIG.P_FILTER_PUBLISHED):
            title_list = self.__unpublished(title_list)
        # Objeto para buscar si el título que ha pedido el usuario
        # está disponible en el archivo word.
        self.quisiste_decir = TitleMgr(title_list)

        # Valores que debo devolver para el objeto html
        # titulo, año, director, duración
        # Los guardo todos en un objeto Pelicula
        self.data = Pelicula()

    def ask_for_data(self):
        # Pido los datos de la película que voy a buscar
        # Titulo
        self.get_ans()

        # Trato de buscar información de esta película en FA.
        FA = Searcher(self.data.titulo)
        FA.print_state()

        while not self.data.director:
            self.data.director = input(self.ASK_DIRECTOR)
            # Si en vez de un director se introduce la dirección de FA, no necesito nada más
            if not self.__interpretate_director(FA.get_url()):
                return

        self.data.año = input(self.ASK_YEAR)
        self.data.duracion = input(self.ASK_DURATION)

    def __interpretate_director(self, suggested_url):

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

    def __get_data_from_FA(self, url):
        # No quiero que se modifique el título que tengo leído.
        # El actual lo he oebtenido del word,
        # Pelicula me puede dar un título de FA que no sea idéntico al que hay en el word
        ori_title = self.data.titulo

        self.data = Pelicula(urlFA=url)
        self.data.get_parsed_page()

        if not self.data.exists():
            return False

        self.data.titulo = ori_title
        self.data.get_director()
        self.data.get_año()
        self.data.get_duracion()
        self.data.get_country()
        return True

    def __unpublished(self, ls_titles):
        # Objeto capaz de leer el csv con todos los títulos publicados
        csv = BlogCsvMgr()
        csv = csv.open_to_read()
        # Elimino la linea de encabezados
        csv.pop(0)
        # Obtengo la lista de títulos,
        # por si están entrecomillados, quito las comillas
        published = [title[0].strip("\"") for title in csv]
        published = [str(title.lower()) for title in published]
        lower_titles = [str(title.lower()) for title in ls_titles]

        ls_unpublished = []
        for i, title in enumerate(lower_titles):
            # Compruebo que no tenga escrito el año
            candidato_año = get_year(title)
            # Tiene escrito el año
            if candidato_año.isnumeric():
                # Quito el año del título
                title = title[:title.rfind('(')]
                # Quito los espacios que hayan podido quedar
                title = title.strip()
                # Compruebo que esté el título en la lista de publicados
                index = all_indices_in_list(published, title)
                # Compruebo que el año sea correcto
                if not any(candidato_año == csv[ocurr][3] for ocurr in index):
                    # Añado el título con las mayúsculas originales
                    ls_unpublished.append(ls_titles[i])

            # No tiene año
            elif title not in published:
                # Añado el título con las mayúsculas originales
                ls_unpublished.append(ls_titles[i])

        return ls_unpublished


    def get_ans_body(self):
        # Función sobreescrita de la clase base
        while not self.data.titulo:
            # Inicializo las variables antes de llamar a input
            self.curr_index = -1
            self.sz_options = self.quisiste_decir.get_suggestions()
            self.n_options = len(self.sz_options)
            # Al llamar a input es cuando me espero que se itilicen las flechas
            self.data.titulo = input(self.ASK_TITLE)
            # Se ha introducido un título, compruebo que sea correcto
            self.data.titulo = self.quisiste_decir.exact_key(self.data.titulo)

        return self.data.titulo


def all_indices_in_list(ls, el):
    '''
    Dado un elemento, lo busco en una lista.
    Devuelvo las posiciones de la lista que contengan al elemento
    '''
    # Incializo la lista que devolveré
    ans_indices = []

    # Itero la lista introducida
    for i, l in enumerate(ls):
        # Compuebo que el elemento actual de la lista sea lo que estoy buscando
        if el == l:
            # Añado el índice actual a la lista que devolveré
            ans_indices.append(i)

    return ans_indices

def get_year(title:str):
    '''
    Dado un título de los escritos en el word,
    quiero extraer el posible título que tenga entre paréntesis
    '''
    # Busco paréntesis en el título introducido
    año_primera_pos = title.rfind("(")
    año_ultima_por = title.rfind(')')

    # Compruebo si he encontrado paréntesis
    if año_primera_pos > 0 and año_ultima_por > 0:
        # Devuelvo lo que haya contenido entre paréntesis
        return title[año_primera_pos + 1:año_ultima_por]
    else:
        # No se ha encontrado año, devuelvo una cadena vacía
        return ""
