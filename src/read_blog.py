import enum
from bs4 import BeautifulSoup


class BlogHiddenData(enum.Enum):
    TITLE = "film-title"
    YEAR = "year"
    DIRECTOR = "director"
    COUNTRY = "pais"
    URL_FA = "link-FA"
    LABELS = "post-labels"
    DURATION = "duration"
    IMAGE = "link-image"

    def get(self, content: BeautifulSoup):
        return content.find(id=self.value)['value']
