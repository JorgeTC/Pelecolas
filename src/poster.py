from datetime import date, datetime, timedelta

from bs4 import BeautifulSoup
from dateutil import tz
from googleapiclient.discovery import Resource
from oauth2client import client

from src.aux_title_str import RE_DATE_DMY, RE_DATE_YMD, RE_TIME
from src.dlg_config import CONFIG
from src.google_api_mgr import GetGoogleApiMgr
from src.read_blog import BlogHiddenData, get_secret_data_from_content


def get_blog_and_api(service: Resource, blog_id: str):
    try:
        # Obtengo la API
        post_api = service.posts()

        # Obtengo el blog que está indicado
        blogs = service.blogs()
        my_blogs = blogs.listByUser(userId='self').execute()
        right_blog = next(
            (blog for blog in my_blogs['items'] if blog['id'] == blog_id), None)

        return right_blog, post_api

    except client.AccessTokenRefreshError:
        print('Error en las credenciales')
        return None, None


class Poster():

    BLOG_ID = CONFIG.get_value(CONFIG.S_POST, CONFIG.P_BLOG_ID)
    SERVICE: Resource = GetGoogleApiMgr('blogger')

    # Guardo el primer mes que tiene reseña
    __first_month = date(2019, 5, 1)

    blog, posts = get_blog_and_api(SERVICE, BLOG_ID)

    @classmethod
    def add_post(cls, content, title, labels):

        # Cuándo se va a publicar la reseña
        str_date = cls.__get_publish_datatime()

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
            f = cls.posts.insert(blogId=cls.BLOG_ID,
                                 body=body, isDraft=bDraft)
            f.execute()
            # Si no está programada como borrador, aviso al usuario de cuándo se va a publicar la reseña
            if not bDraft:
                print(f"La reseña de {title} se publicará el {str_date[:10]}")

        except client.AccessTokenRefreshError:
            print('The credentials have been revoked or expired, please re-run'
                  'the application to re-authorize')

    @classmethod
    def __get_publish_datatime(cls) -> str:
        # Obtengo qué día tengo que publicar la reseña
        sz_date = CONFIG.get_value(CONFIG.S_POST, CONFIG.P_DATE)
        if (match := RE_DATE_DMY.match(sz_date)):
            day = int(match.group(1))
            month = int(match.group(2))
            year = int(match.group(3))
        else:
            # Si no consigo interpretarlo como fecha, le doy la fecha automática
            day, month, year = cls.__get_automatic_date()
        # Obtengo a qué hora tengo que publicar la reseña
        sz_time = CONFIG.get_value(CONFIG.S_POST, CONFIG.P_TIME)
        match = RE_TIME.match(sz_time)
        sz_hour = int(match.group(1))
        sz_minute = int(match.group(2))

        return date_to_str(datetime(year, month, day,
                                    sz_hour, sz_minute))

    @classmethod
    def __get_automatic_date(cls) -> tuple[int, int, int]:

        scheduled = cls.get_scheduled()

        dates = []
        # Extraigo todas las fechas que ya tienen asignado un blog
        for post in scheduled:
            # Leo la fecha
            publish_date = RE_DATE_YMD.match(post['published'])
            year = int(publish_date.group(1))
            month = int(publish_date.group(2))
            day = int(publish_date.group(3))
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
        found = RE_DATE_YMD.match(found)
        year = int(found.group(1))
        month = int(found.group(2))
        day = int(found.group(3))

        return (day, month, year)

    @classmethod
    def get_all_active_posts(cls):
        return cls.get_published_from_date(cls.__first_month)

    @classmethod
    def get_all_posts(cls):

        # Obtengo todos los posts publicados
        posted = cls.get_all_active_posts()

        # Obtengo todos los programados
        scheduled = cls.get_scheduled()

        # Concateno ambas listas
        all_posts = posted + scheduled

        return all_posts

    @classmethod
    def update_post(cls, new_post):

        cls.posts.update(blogId=cls.BLOG_ID,
                         postId=new_post['id'],
                         body=new_post).execute()

    @classmethod
    def get_published_from_date(cls, min_date: date | datetime):

        # Las fechas deben estar introducidas en formato date
        # Las convierto a cadena
        sz_min_date = date_to_str(min_date)

        # Pido los blogs desde entonces
        ls = cls.posts.list(blogId=cls.BLOG_ID,
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

    @classmethod
    def get_scheduled(cls):
        # Hago una lista de todos los posts programados a partir de hoy
        today = datetime.today()
        start_date = date_to_str(today)

        ls = cls.posts.list(blogId=cls.BLOG_ID,
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

    @classmethod
    def get_scheduled_as_list(cls):
        # Quiero una lista de listas.
        ans = []
        # Cada sublista deberá tener 4 elementos:
        # título, link(vacío), director y año
        scheduled = cls.get_scheduled()

        for post in scheduled:
            title = post['title']
            # Parseo el contenido
            body = BeautifulSoup(post['content'], 'html.parser')

            # Extraigo los datos que quiero
            director = get_secret_data_from_content(body, BlogHiddenData.DIRECTOR)
            year = get_secret_data_from_content(body, BlogHiddenData.YEAR)

            ans.append([title, "", director, year])

        return ans


############ aux ################
TIME_ZONE = tz.gettz('Europe/Madrid')
def date_to_str(date: date | datetime):
    '''
    Dada una fecha, devuelvo una cadena
    para poder publicar el post en esa fecha
    '''
    try:
        # Caso en el que esté especificada la hora
        return datetime(date.year, date.month, date.day,
                        date.hour, date.minute,
                        tzinfo=TIME_ZONE).isoformat()
    except AttributeError:
        # Caso en el que no esté especificada la hora
        return datetime(date.year, date.month, date.day,
                        tzinfo=TIME_ZONE).isoformat()
    except:
        return ""
