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


class ReadBlog():

    BLOG_MONTH = 'https://pelecolas.blogspot.com/{}/{:02d}/'.format

    def get_director_year_from_content(self, content: BeautifulSoup):
        '''
        Dado el contenido de un post de mi blog,
        extraigo el año de la película y el director
        '''
        director = content.find(id=BlogHiddenData.DIRECTOR)['value']
        año = content.find(id=BlogHiddenData.YEAR)['value']

        return director, año

    @staticmethod
    def get_secret_data_from_content(content: BeautifulSoup, field):
        return content.find(id=field)['value']
