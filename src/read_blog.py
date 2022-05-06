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

    @staticmethod
    def get(content: BeautifulSoup, field):
        return content.find(id=field)['value']
