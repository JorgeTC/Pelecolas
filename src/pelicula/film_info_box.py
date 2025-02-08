import re

from bs4 import BeautifulSoup

from .pelicula import FAType


class FilmInfoBox:
    '''
    Clase que me devuelve la información que una caja de película contiene.
    Dependiendo de dónde venga la caja, puede tener algunas diferencias.
    La mayoría de campos se pueden encontrar en los mismos lugares.
    El título no aparece igual escrito en un resultado de búsqueda
    y en una lista de películas vistas por un usuario.
    Por eso, esta clase es la base y se debe instanciar una de las clases
    que implementan las distintas versiones de `get_title`.
    '''

    def __init__(self, film_info: BeautifulSoup) -> None:
        # Guardamos el trozo de HTML que contiene la información de la película
        self.film_info = film_info

    def get_title(self) -> str:
        # El título no se puede leer en una caja que venga como un resultado de búsqueda
        # de la misma forma que se lee en una caja que sea una película vista por un usuario.
        # Las clases que hereden de esta tendrán que implementar este método adecuadamente.
        raise NotImplementedError

    def get_FA_url(self) -> str:
        # Devolvemos la dirección enlazada encima del título de la película.
        mc_title = self.film_info.find('div', class_='mc-title')
        return mc_title.find('a')['href']

    def get_year(self) -> int:
        # En este punto la estructura del html cambia en función de si la película tiene los tags animación, cortometraje...
        # Por eso debo hacer una búsqueda
        under_title_info = self.film_info.find(name='div', class_='d-flex')
        year_cont = under_title_info.find(name='span', class_='mc-year')
        str_year = str(year_cont.contents[0])
        return int(re.search(r"(\d{4})", str_year).group(1))

    def get_country(self) -> str:
        # Aunque en la página se muestra como una bandera, en el HTML viene escrito el país.
        return self.film_info.find('img', class_="nflag").attrs['alt']

    def get_directors(self) -> list[str]:
        try:
            directors_div = self.film_info.find('div',
                                                class_="mt-2 mc-director")
            directors_list: list[BeautifulSoup] = directors_div.find_all('a')
        except IndexError:
            return []
        return [director.text
                for director in directors_list]

    def get_director(self) -> str:
        # Obtenemos la lista de directores y devolvemos el primero
        try:
            return self.get_directors()[0]
        except IndexError:
            return ''

    def get_FA_type(self) -> set[FAType]:
        # Obtenemos las etiquetas de la película
        types = self.film_info.find_all('span', class_="type")
        types_str = [type_item.text for type_item in types]

        # Las convertimos al enumerado.
        # Si alguna de las etiquetas no estuviera en el enumerado, obtendríamos un error
        return {FAType(type_str) for type_str in types_str}

    def get_title(self) -> str:
        # Esta caja tiene el mismo campo título y aparece repetido.
        text_a = self.film_info.find('a', class_="d-none d-md-inline-block")
        return text_a.text
