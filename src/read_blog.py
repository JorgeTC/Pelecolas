from bs4 import BeautifulSoup


class BlogHiddenData():
    TITLE = "film-title"
    YEAR = "year"
    DIRECTOR = "director"
    COUNTRY = "pais"
    URL_FA = "link-FA"
    LABELS = "post-labels"
    DURATION = "duration"
    IMAGE = "link-image"


def get_secret_data_from_content(content: BeautifulSoup, field):
    return content.find(id=field)['value']
