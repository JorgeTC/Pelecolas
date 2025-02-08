from bs4 import BeautifulSoup

from src.pelicula import FAType, FilmInfoBox


class FilmBox:
    '''Funciones para extraer datos de la caja de la película'''

    def __init__(self, film_box: BeautifulSoup) -> None:
        self.film_box = film_box
        self.film_info = FilmInfoBox(film_box.find('div', class_="card-body"))

    def get_title(self) -> str:
        return self.film_info.get_title()

    def get_user_note(self) -> int:
        user_vote = self.film_box.find("div",
                                       class_="fa-user-rat-box not-me mx-auto")
        return int(user_vote.text.strip())

    def get_id(self) -> int:
        card = self.film_box.find('div', class_="row movie-card movie-card-1")
        return int(card.attrs['data-movie-id'])

    def get_year(self) -> int:
        return self.film_info.get_year()

    def get_country(self) -> str:
        return self.film_info.get_country()

    def get_directors(self) -> list[str]:
        return self.film_info.get_directors()

    def get_director(self) -> str:
        return self.film_info.get_director()

    def get_FA_type(self) -> set[FAType]:
        return self.film_info.get_FA_type()
