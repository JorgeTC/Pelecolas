from bs4 import BeautifulSoup
from .safe_url import safe_get_url
import urllib.parse

# Clase para guardar los datos que se lean
class TituloYAño():
    def __init__(self, title, year, url):
        self.titulo = title
        self.año = year
        self.url = url

################ MACROS CLASIFICAR LA PÁGINA ################
ENCONTRADA = 1
VARIOS_RESULTADOS = 2
NO_ENCONTRADA = 3
ERROR = 4
#############################################################

class Searcher():
    URL_SEARCH = "https://www.filmaffinity.com/es/search.php?stext={}"
    def __init__(self, to_search):
        self.title = to_search

        # Busco si lo introducido contiene un año.
        año_primera_pos = self.title.rfind("(")
        año_ultima_por = self.title.rfind(')')
        candidato_año = self.title[año_primera_pos + 1:año_ultima_por]
        # Es posible que hay acosas entre paréntesis qeu no sea un año.
        # Por eso, compruebo que aquello que está entre paréntesis sean números.
        if año_primera_pos > 0 and año_ultima_por > 0 and str(candidato_año).isnumeric():
            self.año = int(candidato_año)
        else:
            self.año = 0
            # Sé que no he encontrado un año.
            # Guardo el código de no encontrado, -1.
            año_primera_pos = -1

        # Modifico el título para guardar el título sin el año.
        if año_primera_pos != -1:
            self.title = self.title[:año_primera_pos]
        self.title = self.title.strip()

        # Creo la url para buscar ese título
        self.search_url = self.__get_search_url()

        # Creo una variable para cuando encuentre a película
        self.film_url = ''
        self.__coincidente = None

        # Guardo la página de búsqueda parseada.
        req = safe_get_url(self.search_url)
        self.parsed_page = BeautifulSoup(req.text,'html.parser')

        # Ya he hecho la búsqueda.
        # Quiero saber qué se ha conseguido, en qué caso estamos.
        # Antes de hacer esta distinción, necesito ver si FilmAffinity me ha redirigido.
        self.__get_redirected_url()
        self.__estado = self.__clarify_case()

    def __get_search_url(self):
        # Convierto los caracteres no alfanuméricpos en hexadecimal
        # No puedo convertir los espacios:
        # FilmAffinity convierte los espacios en +.
        title_for_url = urllib.parse.quote(self.title, safe=" ")

        # Cambio los espacios para poder tener una sola url
        title_for_url = title_for_url.replace(" ", "+")

        # Devuelvo la dirección de búsqueda
        return self.URL_SEARCH.format(title_for_url)

    def __search_boxes(self):

        # Sólo tengo un listado de películas encontradas cuando tenga muchos resultados.
        if self.__estado != VARIOS_RESULTADOS:
            return

        # Caja donde están todos los resultados
        peliculas_encontradas = self.parsed_page.find_all('div',{'class': "z-search"})
        # Se han hecho tres búsquedas: título, director, reparto
        # la única que me interesa es la primera: título.
        peliculas_encontradas = peliculas_encontradas[0]
        peliculas_encontradas = peliculas_encontradas.find_all('div')
        peliculas_encontradas = [div for div in peliculas_encontradas if div.get('class')[0] == 'se-it']

        lista_peliculas = []
        curr_year = 0

        for p in peliculas_encontradas:
            # Leo el año...
            if len(p.get('class')) > 1:
                year = p.find('div', {'class' : 'ye-w'})
                curr_year = int(year.contents[0])

            # ...si no encuentro el año, el año que ya tengo leído me sirve.

            # Leo el título y el enlace
            title_box = p.find('div', {'class' : 'mc-title'})
            url = title_box.contents[0].previous_element.contents[0].attrs['href']
            title = title_box.contents[0].previous_element.contents[0].attrs['title']
            title = title.strip()

            # Lo añado a la lista
            lista_peliculas.append(TituloYAño(title,curr_year,url))

        return lista_peliculas

    def __clarify_case(self):

        # Ya me han redireccionado
        # Mirando la url puedo distinguir los tres casos.
        # Me quedo con la información inmediatamente posterior al idioma.
        stage = self.film_url[32:]

        # El mejor de los casos, he encontrado la película
        if stage.find('film') >= 0:
            return ENCONTRADA
        if stage.find('advsearch') >= 0:
            return NO_ENCONTRADA
        if stage.find('search') >= 0:
            return VARIOS_RESULTADOS

        return ERROR

    def __get_redirected_url(self):
        self.film_url = self.parsed_page.find('meta', property='og:url')['content']

    def encontrada(self):
        return self.__estado == ENCONTRADA

    def resultados(self):
        # Comprobar si hay esperanza de encontrar la ficha
        return self.__estado == ENCONTRADA or self.__estado == VARIOS_RESULTADOS

    def get_url(self):
        # Una vez hechas todas las consideraciones,
        # me devuelve la ficha de la película que ha encontrado.
        if self.__estado == ENCONTRADA:
            return self.film_url

        if self.__estado == VARIOS_RESULTADOS:
            lista_peliculas = self.__search_boxes()
            self.film_url = self.__elegir_url(lista_peliculas)
            return self.film_url

        # No he sido capaz de encontrar nada
        return ""

    def __elegir_url(self, lista):
        # Tengo una lista de películas con sus años.
        # Miro cuál de ellas me sirve más.

        # Guardo todas las que sean coincidentes.
        # Espero que sólo sea una.
        coincidentes = []

        # Itero las películas candidatas
        for candidato in lista:
            # Si el año no coincide, no es esta la película que busco
            if self.año and self.año != candidato.año:
                continue

            # Si el título coincide, devuelvo esa url.
            if self.title.lower() == candidato.titulo.lower():
                coincidentes.append(candidato)

        # Una vez hecha la búsqueda, miro cuántas películas me sirven.
        if len(coincidentes) == 1:
            self.__coincidente = coincidentes[0]
            return self.__coincidente.url
        else:
            # Hay varios candidatos igual de válidos.
            # no puedo devolver nada con certeza.
            return ""

    def print_state(self):

        # Si no se ha encontrado nada, no hay nada que imprimir
        if not self.resultados():
            return

        # He encontrado la película
        if self.__estado == ENCONTRADA:
            print("Se ha encontrado una única película llamada", self.title)
            return

        # Tengo varias películas
        # if self.__estado == VARIOS_RESULTADOS:
        # Llamo al cálculo de self.film_url
        self.get_url()
        if self.film_url:
            print("Se ha encontrado una única película llamada", self.title, \
                "del año", self.__coincidente.año)




if __name__ == '__main__':
    # searc = Searcher("El milagro de P. Tinto")
    searc = Searcher("caza")
    searc.get_url()