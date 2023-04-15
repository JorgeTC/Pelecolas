from .quoter_director import QuoterDirector
from .quoter_title import QuoterTitle


class Quoter:
    def __init__(self, titulo: str, director: str):
        # Guardo los datos de la película actual
        self.quoter_title = QuoterTitle(titulo)
        self.quoter_director = QuoterDirector(director)

    def quote_parr(self, text: str) -> str:
        text = self.quoter_title.quote_titles(text)
        text = self.quoter_director.quote_directors(text)
        return text

    @property
    def quoted_directors(self) -> set[str]:
        return self.quoter_director._quoted_directors

    @property
    def quoted_titles(self) -> set[str]:
        return self.quoter_title._quoted_titles

