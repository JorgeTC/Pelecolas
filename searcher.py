from bs4 import BeautifulSoup
from safe_url import safe_get_url

# Clase para guardar los datos que se lean
class TituloYAño():
    def __init__(self, title, year):
        self.titulo = title
        self.año = year

################ MACROS CLASIFICAR LA PÁGINA ################
ENCONTRADA = 1
VARIOS_RESULTADOS = 2
NO_ENCONTRADA = 3
ERROR = 4
#############################################################

class Searcher():
    def __init__(self, to_search):
        self.title = to_search

        año_primera_pos = self.title.rfind("(")
        if año_primera_pos != -1:
            self.title = self.title[:año_primera_pos]
        self.title.strip()

        # Creo la url para buscar ese título
        # Cambio los espacios para poder tener una sola url
        self.title =self.title.replace(" ", "+")
        # Añado el prefijo
        pref = "https://www.filmaffinity.com/es/search.php?stext="
        self.search_url = pref + self.title

        # Creo una variable para cuando encuentre a película
        self.film_url = ''

        req = safe_get_url(self.search_url)
        self.parsed_page = BeautifulSoup(req.text,'html.parser')

        self.get_url()
        self.__estado = self.clarify_case()

    def get_boxes(self):

        if self.__estado != VARIOS_RESULTADOS:
            return

        # Caja donde están todos los resultados
        peliculas_encontradas = self.parsed_page.find_all('div',{'class': "z-search"})
        len(peliculas_encontradas)

    def clarify_case(self):

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

    def get_url(self):
        self.film_url = self.parsed_page.find('meta', property='og:url')['content']

    def encontrada(self):
        return self.__estado == ENCONTRADA

    def resultados(self):
        # Comprobar si hay esperanza de encontrar la ficha
        return self.__estado == ENCONTRADA or self.__estado == VARIOS_RESULTADOS




if __name__ == '__main__':
    # searc = Searcher("El milagro de P. Tinto")
    searc = Searcher("caza")
    searc.get_boxes()