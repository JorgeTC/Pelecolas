
from bs4 import BeautifulSoup
import pandas as pd
from openpyxl.styles import Alignment, Font
from .ProgressBar import ProgressBar
from .safe_url import safe_get_url
from .Pelicula import Pelicula

class Writer(object):
    def __init__(self, id, worksheet):
        # numero de usuario en string
        self.id_user = str(id)
        # Contador de peliculas
        self.film_index = 0
        # Numero de pagina actual
        self.page_index = 0

        # Barra de progreso
        self.bar = ProgressBar()

        # Descargo la propia página actual. Es una página "de fuera".
        self.soup_page = None
        # Lista de peliculas que hay en la página actual
        self.film_list = []
        #Inicializo las dos variables
        self.next_page()

        # Votaciones en total
        self.total_films = self.get_total_films()
        # Hoja de excel
        self.ws = worksheet

        # DataFrame para guardar los datos antes de volcarlos al excel
        self.df = pd.DataFrame(columns=['Id', 'User Note', 'Duration', 'Note FA', 'Voters'])

    def get_total_films(self):
        # me espero que haya un único "value-box active-tab"
        mydivs = self.soup_page.find("a", {"class": "value-box active-tab"})
        stringNumber = mydivs.contents[3].contents[1]
        # Elimino el punto de los millares
        stringNumber = stringNumber.replace('.','')
        return int(stringNumber)

    def get_list_url(self, page_index):
        sz_ans = 'https://www.filmaffinity.com/es/userratings.php?user_id=' + self.id_user + '&p='
        sz_ans = sz_ans + str(page_index) + '&orderby=4'

        return sz_ans

    def next_page(self):

        self.film_index += len(self.film_list)
        if self.film_index:
            self.bar.update(self.film_index/self.total_films)

        # Anavanzo a la siguiente página
        self.page_index += 1
        url = self.get_list_url(self.page_index)
        resp = safe_get_url(url)
        # Guardo la página ya parseada
        self.soup_page = BeautifulSoup(resp.text,'html.parser')
        # Leo todas las películas que haya en ella
        self.film_list = self.soup_page.findAll("div", {"class": "user-ratings-movie"})

    def read_watched(self):
        # Creo una barra de progreso
        self.bar.timer.reset()

        # Itero hasta que haya leído todas las películas
        while (self.film_index < self.total_films):
            # Itero las películas en mi página actual
            for film in self.film_list:
                self.read_film(film)

            self.next_page()

        for index, row in self.df.iterrows():
            self.write_in_excel(index, row)

    def add_to_df(self, film):

        film.get_time_and_FA()

        self.df = self.df.append({'Id' : film.id,
                        'User Note' : film.user_note,
                        'Duration' : film.duracion,
                        'Voters' : film.votantes_FA,
                        'Note FA' : film.nota_FA}, ignore_index=True)

    def read_film(self, film):
        # Convierto lo leído de la página a un objeto película
        film = Pelicula(movie_box=film)

        # Compruebo que su título sea válido
        if not film.valid():
            return

        # Escribo sus datos en el excel
        self.add_to_df(film)


    def write_in_excel(self, line, film):

        # La enumeración empezará en 0,
        # pero sólo esribimos datos a partir de la segunda linea.
        line = line + 2

        # La votacion del usuario la leo desde fuera
        # no puedo leer la nota del usuario dentro de la ficha
        UserNote = film['User Note']
        self.set_cell_value(line, 2, int(UserNote))
        self.set_cell_value(line, 10, str("=B" + str(line) + "+RAND()-0.5"))
        self.set_cell_value(line, 11, "=(B" + str(line) + "-1)*10/9")
        # En la primera columna guardo la id para poder reconocerla
        self.set_cell_value(line, 1, int(film['Id']))

        if (film['Duration'] != 0):
            # dejo la casilla en blanco si no logra leer ninguna duración de FA
            self.set_cell_value(line, 4, film['Duration'])
        if (film['Note FA'] != 0):
            # dejo la casilla en blanco si no logra leer ninguna nota de FA
            self.set_cell_value(line, 3, film['Note FA'])
            self.set_cell_value(line, 6, "=ROUND(C" + str(line) + "*2, 0)/2")
            self.set_cell_value(line, 7, "=B" + str(line) + "-C" + str(line))
            self.set_cell_value(line, 8, "=ABS(G" + str(line) + ")")
            self.set_cell_value(line, 9, "=IF($G" + str(line) + ">0,1,0.1)")
            self.set_cell_value(line, 12, "=(C" + str(line) + "-1)*10/9")
        if (film['Voters'] != 0):
            # dejo la casilla en blanco si no logra leer ninguna votantes
            self.set_cell_value(line, 5, film['Voters'])


    def set_cell_value(self, line, col, value):
        cell = self.ws.cell(row = line, column=col)
        cell.value = value
        # Configuramos el estilo de la celda atendiendo a su columna
        # visionados. Ponemos punto de millar
        if (col == 5):
            cell.number_format = '#,##0'
        # booleano mayor que
        elif (col == 9):
            cell.number_format = '0'
            cell.font = Font(name = 'SimSun', bold = True)
            cell.alignment=Alignment(horizontal='center', vertical='center')
        # Nota del usuario más el ruido
        elif (col == 10):
            cell.number_format = '0.0'
        #reescala
        elif (col == 11 or col == 12):
            cell.number_format = '0.00'

    def next_film(self):
        self.film_index += 1
        self.bar.update(self.film_index/self.total_films)
