from bs4 import BeautifulSoup
import sys
sys.path.append("../")
from .safe_url import safe_get_url


class Pelicula(object):
    def __init__(self, urlFA=None):
        self.url_FA = str(urlFA)
        resp = safe_get_url(self.url_FA)
        if resp.status_code == 404:
            self.exists = False
            return  # Si el id no es correcto, dejo de construir la clase
        else:
            self.exists = True

        # Parseo la página
        self.parsed_page = BeautifulSoup(resp.text,'html.parser')

        self.director = None
        self.año = None
        self.duración = None

    def GetDirectorYearDuration(self):

        l = self.parsed_page.find(id="left-column")
        try:
            self.duración = l.find(itemprop="duration").contents[0]
        except:
            return False
            # caso en el que no está escrita la duración
        # quito el sufijo min.
        self.duración = int(self.duración.split(' ', 1)[0])

        try:
            self.director = l.find(itemprop="director").contents[0].contents[0].contents[0]
        except:
            return False

        try:
            self.año = l.find(itemprop="datePublished").contents[0]
        except:
            return False
