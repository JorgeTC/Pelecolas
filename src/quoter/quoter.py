from src.quoter.quoter_director import QuoterDirector
from src.quoter.quoter_title import QuoterTitle


class Quoter:
    def __init__(self, titulo: str, director: str):
        # Guardo los datos de la película actual
        self.quoter_title = QuoterTitle(titulo)
        self.quoter_director = QuoterDirector(director)

    def quote_parr(self, text: str) -> str:
        text = self.quoter_title.quote_titles(text)
        text = self.quoter_director.quote_directors(text)
        return text

    def get_quoted_directors(self) -> set[str]:
        return self.quoter_director._QuoterDirector__quoted_directors

    def get_quoted_titles(self) -> set[str]:
        return self.quoter_title._QuoterTitle__quoted_title

    def clear_questions(self) -> None:
        self.quoter_director.clear_questions()
