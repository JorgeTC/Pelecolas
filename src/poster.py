from datetime import datetime, timedelta

import pytz
from bs4 import BeautifulSoup
from oauth2client import client

from src.dlg_config import CONFIG
from src.google_api_mgr import GoogleApiMgr
from src.read_blog import ReadBlog


class Poster(ReadBlog, GoogleApiMgr):

    BLOG_ID = CONFIG.get_value(CONFIG.S_POST, CONFIG.P_BLOG_ID)

    def __init__(self):
        # Inicializo la clase madre
        GoogleApiMgr.__init__(self, 'blogger')

        try:
            blogs = self.SERVICE.blogs()

            # Retrieve the list of Blogs this user has write privileges on
            thisusersblogs = blogs.listByUser(userId='self').execute()

            self.posts = self.SERVICE.posts()

            for blog in thisusersblogs['items']:
                if blog['id'] == self.BLOG_ID:
                    self.blog = blog

        except client.AccessTokenRefreshError:
            print('The credentials have been revoked or expired, please re-run'
                  'the application to re-authorize')

    def add_post(self, content, title, labels):

        # Compruebo que el blog que tengo guardado sea el correcto
        if self.blog['id'] != self.BLOG_ID:
            return False

        # Cuándo se va a publicar la reseña
        str_date = self.__get_publish_datatime()

        # Creo el contenido que voy a publicar
        body = {
            "kind": "blogger#post",
            "title": title,
            "content": content,
            "published": str_date
        }
        # Solo añado las etiquetas si son válidas
        if labels:
            body["labels"] = labels

        try:
            # Miro si la configuración me pide que lo publique como borrador
            bDraft = CONFIG.get_bool(CONFIG.S_POST, CONFIG.P_AS_DRAFT)
            f = self.posts.insert(blogId=self.BLOG_ID,
                                  body=body, isDraft=bDraft)
            f.execute()
            # Si no está programada como borrador, aviso al usuario de cuándo se va a publicar la reseña
            if not bDraft:
                print("La reseña de {} se publicará el {}".format(title, str_date[:10]))

        except client.AccessTokenRefreshError:
            print('The credentials have been revoked or expired, please re-run'
                  'the application to re-authorize')

    def __get_publish_datatime(self):
        # Obtengo qué día tengo que publicar la reseña
        sz_date = CONFIG.get_value(CONFIG.S_POST, CONFIG.P_DATE)
        if sz_date.lower() == 'auto':
            day, month, year = self.__get_automatic_date()
        else:
            sz_date = sz_date.split("/")
            day = int(sz_date[0])
            month = int(sz_date[1])
            year = int(sz_date[2])
        # Obtengo a qué hora tengo que publicar la reseña
        sz_time = CONFIG.get_value(CONFIG.S_POST, CONFIG.P_TIME)
        sz_hour = int(sz_time.split(":")[0])
        sz_minute = int(sz_time.split(":")[1])

        return date_to_str(datetime(year, month, day,
                                    sz_hour, sz_minute))

    def __get_automatic_date(self):

        scheduled = self.get_scheduled()

        dates = []
        # Extraigo todas las fechas que ya tienen asignado un blog
        for post in scheduled:
            # Leo la fecha
            publish_date = post['published']
            year = int(publish_date[0:4])
            month = int(publish_date[5:7])
            day = int(publish_date[8:10])
            publish_date = str(datetime(year, month, day).date())
            # La añado a mi lista
            dates.append(publish_date)

        # Busco los viernes disponibles
        # Voy al próximo viernes
        today = datetime.today().date()
        week_day = today.weekday()
        days_till_next_friday = (4 - week_day) % 7
        next_friday = today + timedelta(days=days_till_next_friday)

        # Avanzo por los viernes hasta encontrar uno que esté disponible
        found = ""
        while not found:
            # Convierto a string
            str_next_friday = str(next_friday)
            # Si no se encuentra entre las fechas con reseña, he econtrado un viernes disponible
            if str_next_friday not in dates:
                found = str_next_friday
            # Avanzo al siguiente viernes
            next_friday = next_friday + timedelta(days=7)

        # Devuelvo la fecha encontrada como números
        year = int(found[0:4])
        month = int(found[5:7])
        day = int(found[8:10])

        return (day, month, year)

    def get_published_from_date(self, min_date):

        # Las fechas deben estar introducidas en formato date
        # Las convierto a cadena
        sz_min_date = date_to_str(min_date)

        # Pido los blogs desde entonces
        ls = self.posts.list(blogId=self.BLOG_ID,
                             status='LIVE',
                             startDate=sz_min_date,
                             maxResults=500)
        execute = ls.execute()

        # Obtengo todos los posts que están programados
        try:
            scheduled = execute['items']
        except:
            scheduled = []

        return scheduled

    def get_scheduled(self):
        # Hago una lista de todos los posts programados a partir de hoy
        today = datetime.today()
        start_date = date_to_str(today)

        ls = self.posts.list(blogId=self.BLOG_ID,
                             maxResults=55,
                             status='SCHEDULED',
                             startDate=start_date)
        execute = ls.execute()

        # Obtengo todos los posts que están programados
        try:
            scheduled = execute['items']
        except:
            scheduled = []

        return scheduled

    def get_scheduled_as_list(self):
        # Quiero una lista de listas.
        ans = []
        # Cada sublista deberá tener 4 elementos:
        # título, link(vacío), director y año
        scheduled = self.get_scheduled()

        for post in scheduled:
            title = post['title']
            # Parseo el contenido
            body = BeautifulSoup(post['content'], 'html.parser')

            # Extraigo los datos que quiero
            director, year = self.get_director_year_from_content(body)

            ans.append([title, "", director, year])

        return ans


##### Creo un objeto global #####
POSTER = Poster()
#################################

############ aux ################
def date_to_str(date):
    '''
    Dada una fecha, devuelvo una cadena
    para poder publicar el post en esa fecha
    '''
    try:
        # Caso en el que esté especificada la hora
        return datetime(date.year, date.month, date.day,
                        date.hour, date.minute,
                        tzinfo=pytz.UTC).isoformat()
    except AttributeError:
        # Caso en el que no esté especificada la hora
        return datetime(date.year, date.month, date.day,
                        tzinfo=pytz.UTC).isoformat()
    except:
        return ""
