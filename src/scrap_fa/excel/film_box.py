import re

from bs4 import BeautifulSoup, Tag


class FilmBox:
    '''Funciones para extraer datos de la caja de la película'''

    def __init__(self, film_box: BeautifulSoup) -> None:
        self.film_box = film_box

    def get_title(self) -> str:
        return self.film_box.contents[1].contents[1].contents[3].contents[1].contents[0].contents[0]

    def get_user_note(self) -> int:
        return int(self.film_box.contents[3].contents[1].contents[1].contents[0])

    def get_id(self) -> int:
        return int(self.film_box.contents[1].contents[1].attrs['data-movie-id'])

    def get_year(self) -> int:
        # Accedo a la parte que es común en todas las cajas
        info_container: BeautifulSoup = self.film_box.contents[1].contents[1].contents[3]
        # En este punto la estructura del html cambia en función de si la película tiene los tags animación, cortometraje...
        # Por eso debo hacer una búsqueda
        under_title_info = info_container.find(name='div', class_='d-flex')
        year_cont = under_title_info.find(name='span', class_='mc-year')
        str_year = str(year_cont.contents[0])
        return int(re.search(r"(\d{4})", str_year).group(1))

    def get_country(self) -> str:
        return self.film_box.contents[1].contents[1].contents[3].contents[3].contents[1].attrs['alt']

    def get_directors(self) -> list[str]:
        try:
            directors = self.film_box.contents[1].contents[1].contents[3].contents[7].contents[1].contents
        except IndexError:
            return []
        return [director.contents[0].contents[0]
                for director in directors
                if isinstance(director, Tag)]

    def get_director(self) -> str:
        try:
            return self.get_directors()[0]
        except IndexError:
            return ''
