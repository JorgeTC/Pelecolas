import re

from bs4 import BeautifulSoup


class FilmBox:
    '''Funciones para extraer datos de la caja de la película'''

    def __init__(self, film_box: BeautifulSoup) -> None:
        self.film_box = film_box
        self.film_info = film_box.find('div', class_="card-body")

    def get_title(self) -> str:
        text_a = self.film_info.find('a', class_="d-none d-md-inline-block")
        return text_a.text

    def get_user_note(self) -> int:
        user_vote = self.film_box.find("div", class_="fa-user-rat-box not-me mx-auto")
        return int(user_vote.text.strip())

    def get_id(self) -> int:
        card = self.film_box.find('div', class_="row movie-card movie-card-1")
        return int(card.attrs['data-movie-id'])

    def get_year(self) -> int:
        # En este punto la estructura del html cambia en función de si la película tiene los tags animación, cortometraje...
        # Por eso debo hacer una búsqueda
        under_title_info = self.film_info.find(name='div', class_='d-flex')
        year_cont = under_title_info.find(name='span', class_='mc-year')
        str_year = str(year_cont.contents[0])
        return int(re.search(r"(\d{4})", str_year).group(1))

    def get_country(self) -> str:
        return self.film_info.find('img', class_="nflag").attrs['alt']

    def get_directors(self) -> list[str]:
        try:
            directors_div = self.film_info.find('div', class_="mt-2 mc-director")
            directors_list: list[BeautifulSoup] = directors_div.find_all('a')
        except IndexError:
            return []
        return [director.text
                for director in directors_list]

    def get_director(self) -> str:
        try:
            return self.get_directors()[0]
        except IndexError:
            return ''
