
import concurrent.futures
from math import ceil

from bs4 import BeautifulSoup
from openpyxl.styles import Alignment, Font
from pandas.core.frame import DataFrame

from . import url_FA
from .Pelicula import Pelicula
from .ProgressBar import ProgressBar
from .safe_url import safe_get_url


class Writer(object):

    columns = ["Id", "Mia", "FA", "Duracion", "Visionados",
            "FA redondeo", "Diferencia", "Diferencia abs", "Me ha gustado",
            "Mia + ruido", "FA + ruido", "Mia rees", "FA rees"]
    columns = dict(zip(columns, range(1,len(columns)+1)))

    def __init__(self, id, worksheet):
        # numero de usuario en string
        self.id_user = str(id)
        # Contador de peliculas
        self.film_index = 0
        # Numero de pagina actual
        self.page_index = 1

        # Barra de progreso
        self.bar = ProgressBar()

        # Descargo la propia página actual. Es una página "de fuera".
        self.soup_page = None
        # Lista de peliculas que hay en la página actual
        self.film_list = []

        # Votaciones en total
        self.total_films = self.get_total_films()
        # Rellenar la lista de film_list
        self.__get_all_boxes()
        # Hoja de excel
        self.ws = worksheet

    def get_total_films(self):

        url = self.get_list_url(self.page_index)
        resp = safe_get_url(url)
        # Guardo la página ya parseada
        self.soup_page = BeautifulSoup(resp.text,'html.parser')

        # me espero que haya un único "value-box active-tab"
        mydivs = self.soup_page.find("a", {"class": "value-box active-tab"})
        stringNumber = mydivs.contents[3].contents[1]
        # Elimino el punto de los millares
        stringNumber = stringNumber.replace('.','')
        return int(stringNumber)

    def __get_all_boxes(self):
        n_pages = ceil(self.total_films / 20)
        url_pages = [self.get_list_url(i + 1) for i in range(n_pages)]

        executor = concurrent.futures.ThreadPoolExecutor()
        self.film_list = list(executor.map(self.__list_boxes, url_pages))


    def __list_boxes(self, url):
        resp = safe_get_url(url)
        # Guardo la página ya parseada
        soup_page = BeautifulSoup(resp.text,'html.parser')
        # Leo todas las películas que haya en ella
        return list(soup_page.findAll("div", {"class": "user-ratings-movie"}))

    def get_list_url(self, page_index):
        # Compongo la url dado el usuario y el índice
        return url_FA.URL_USER_PAGE(self.id_user, str(page_index))

    def __next_page(self):


        self.film_index += len(self.film_list[self.page_index-1])
        if self.film_index:
            self.bar.update(self.film_index/self.total_films)

        # Anavanzo a la siguiente página
        self.page_index += 1

    def read_watched(self):
        # Creo un objeto para hacer la gestión de paralelización
        executor = concurrent.futures.ThreadPoolExecutor(max_workers=20)
        # Creo una lista de listas donde se guardarán los datos de las películas
        rows_data=[]

        # Creo una barra de progreso
        self.bar.reset_timer()

        # Itero hasta que haya leído todas las películas
        while (self.film_index < self.total_films):
            # Lsita de las películas válidas en la página actual.
            # No puedo modificar self.film_list
            valid_film_list = [Pelicula(box) for box in self.film_list[self.page_index-1]]
            valid_film_list = [film for film in valid_film_list if film.valid()]

            # Itero las películas en mi página actual
            rows_data += list(executor.map(self.__read_film, valid_film_list))

            # Avanzo a la siguiente página de películas vistas por el usuario
            self.__next_page()

        df = DataFrame(rows_data,
                        columns=['Id', 'User Note', 'Duration', 'Voters', 'Note FA', 'Title'])

        for index, row in df.iterrows():
            self.__write_in_excel(index, row)

    def __read_film(self, film : Pelicula):
        # Hacemos la parte más lenta, que necesita parsear la página.
        film.get_time_and_FA()

        # Es importante este orden porque debe coincidir
        # con los encabezados del DataFrame que generaremos
        return [film.id,
                film.user_note,
                film.duracion,
                film.votantes_FA,
                film.nota_FA,
                film.titulo]


    def __write_in_excel(self, line, film):

        # La enumeración empezará en 0,
        # pero sólo esribimos datos a partir de la segunda linea.
        line = line + 2

        # La votacion del usuario la leo desde fuera
        # no puedo leer la nota del usuario dentro de la ficha
        UserNote = film['User Note']
        self.__set_cell_value(line, self.columns["Mia"],
                                int(UserNote))
        self.__set_cell_value(line, self.columns["Mia + ruido"],
                                "=B{}+RAND()-0.5".format(line))
        self.__set_cell_value(line, self.columns["Mia rees"],
                                "=(B{}-1)*10/9".format(line))
        # En la primera columna guardo la id para poder reconocerla
        self.__set_cell_value(line, self.columns["Id"],
                                film['Title'], int(film['Id']))

        if (film['Duration'] != 0):
            # dejo la casilla en blanco si no logra leer ninguna duración de FA
            self.__set_cell_value(line, self.columns["Duracion"],
                                    film['Duration'])
        if (film['Note FA'] != 0):
            # dejo la casilla en blanco si no logra leer ninguna nota de FA
            self.__set_cell_value(line, self.columns["FA"],
                                    film['Note FA'])
            self.__set_cell_value(line, self.columns["FA redondeo"],
                                    "=ROUND(C{}*2, 0)/2".format(line))
            self.__set_cell_value(line, self.columns["Diferencia"],
                                    "=B{0}-C{0}".format(line))
            self.__set_cell_value(line, self.columns["Diferencia abs"],
                                    "=ABS(G{})".format(line))
            self.__set_cell_value(line, self.columns["Me ha gustado"],
                                    "=IF($G{}>0,1,0.1)".format(line))
            self.__set_cell_value(line, self.columns["FA rees"],
                                    "=(C{}-1)*10/9".format(line))
            self.__set_cell_value(line, self.columns["FA + ruido"],
                                    "=C{}+(RAND()-0.5)/10".format(line))
        if (film['Voters'] != 0):
            # dejo la casilla en blanco si no logra leer ninguna votantes
            self.__set_cell_value(line, self.columns["Visionados"],
                                    film['Voters'])


    def __set_cell_value(self, line, col, value, id=0):
        cell = self.ws.cell(row = line, column=col)
        cell.value = value
        # Configuramos el estilo de la celda atendiendo a su columna
        # visionados. Ponemos punto de millar
        if (col == self.columns["Visionados"]):
            cell.number_format = '#,##0'
        # booleano mayor que
        elif (col == self.columns["Me ha gustado"]):
            cell.number_format = '0'
            cell.font = Font(name = 'SimSun', bold = True)
            cell.alignment=Alignment(horizontal='center', vertical='center')
        # Nota del usuario más el ruido
        elif (col == self.columns["Mia + ruido"]):
            cell.number_format = '0.0'
        # Nota de FA más el ruido
        elif (col == self.columns["FA + ruido"]):
            cell.number_format = '0.00'
        #reescala
        elif (col == self.columns["Mia rees"] or
              col == self.columns["FA rees"]):
            cell.number_format = '0.00'
        # Nombre de la película con un hipervínculo
        elif (col == self.columns["Id"]):
            # Añado un hipervínculo a su página
            cell.style = 'Hyperlink'
            cell.hyperlink = url_FA.URL_FILM_ID(id)
            # Fuerzo el formato como texto
            cell.number_format = '@'

