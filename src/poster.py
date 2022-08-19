from dataclasses import asdict
from datetime import date, datetime, timedelta

from bs4 import BeautifulSoup
from dateutil import tz
from googleapiclient.discovery import Resource
from oauth2client import client

from src.api_dataclasses import Blog, Post
from src.aux_title_str import DMY, date_from_DMY, date_from_YMD, time_from_str
from src.config import Config, Param, Section
from src.google_api_mgr import GetGoogleApiMgr
from src.read_blog import BlogHiddenData


def get_blog_and_api(service: Resource, blog_id: str) -> tuple[Blog, Resource]:
    try:
        # Obtengo la API
        post_api = service.posts()

        # Obtengo el blog que está indicado
        blogs = service.blogs()
        my_blogs = blogs.listByUser(userId='self').execute()
        right_blog = next(
            (blog for blog in my_blogs['items'] if blog['id'] == blog_id), None)
        right_blog = Blog(**right_blog)

        return right_blog, post_api

    except client.AccessTokenRefreshError:
        print('Error en las credenciales')
        return None, None


class Poster():

    BLOG_ID = Config.get_value(Section.POST, Param.BLOG_ID)
    SERVICE: Resource = GetGoogleApiMgr('blogger')

    # Guardo el primer mes que tiene reseña
    __first_month = date(2019, 5, 1)

    blog, posts = get_blog_and_api(SERVICE, BLOG_ID)

    @classmethod
    def add_post(cls, content: str, title: str, labels: str):

        # Cuándo se va a publicar la reseña
        str_date = cls.__get_publish_datatime()

        # Creo el contenido que voy a publicar
        body = Post(title=title,
                    content=content,
                    published=str_date)
        # Solo añado las etiquetas si son válidas
        if labels:
            body.labels = labels

        # Miro si la configuración me pide que lo publique como borrador
        bDraft = Config.get_bool(Section.POST, Param.AS_DRAFT)
        try:
            f = cls.posts.insert(blogId=cls.BLOG_ID,
                                 body=asdict(body), isDraft=bDraft)
            f.execute()
            # Si no está programada como borrador, aviso al usuario de cuándo se va a publicar la reseña
            if not bDraft:
                print(f"La reseña de {title} "
                      f"se publicará el {DMY(str_date[:10])}")

        except client.AccessTokenRefreshError:
            print('The credentials have been revoked or expired, please re-run'
                  'the application to re-authorize')

    @classmethod
    def __get_publish_datatime(cls) -> str:
        # Obtengo qué día tengo que publicar la reseña
        sz_date = Config.get_value(Section.POST, Param.DATE)
        if not (publish_date := date_from_DMY(sz_date)):
            # Si no consigo interpretarlo como fecha, le doy la fecha automática
            publish_date = cls.__get_automatic_date()

        # Obtengo a qué hora tengo que publicar la reseña
        sz_time = Config.get_value(Section.POST, Param.TIME)
        time = time_from_str(sz_time)

        return date_to_str(datetime.combine(publish_date, time))

    @classmethod
    def __get_automatic_date(cls) -> date:

        scheduled = cls.get_scheduled()

        # Extraigo todas las fechas que ya tienen asignado un blog
        dates = {str(date_from_YMD(post.published)) for post in scheduled}

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
            # Si no se encuentra entre las fechas con reseña, he encontrado un viernes disponible
            if str_next_friday not in dates:
                found = str_next_friday
            # Avanzo al siguiente viernes
            next_friday = next_friday + timedelta(days=7)

        # Devuelvo la fecha encontrada como fecha
        return date_from_YMD(found)

    @classmethod
    def get_all_active_posts(cls) -> list[Post]:
        return cls.get_published_from_date(cls.__first_month)

    @classmethod
    def get_all_posts(cls) -> list[Post]:

        # Obtengo todos los posts publicados
        posted = cls.get_all_active_posts()

        # Obtengo todos los programados
        scheduled = cls.get_scheduled()

        # Concateno ambas listas
        all_posts = posted + scheduled

        return all_posts

    @classmethod
    def update_post(cls, new_post: Post):

        cls.posts.update(blogId=cls.BLOG_ID,
                         postId=new_post.id,
                         body=asdict(new_post)).execute()

    @classmethod
    def get_published_from_date(cls, min_date: date | datetime) -> list[Post]:

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
            scheduled = [Post(**item) for item in execute['items']]
        except:
            scheduled = []

        return scheduled

    @classmethod
    def get_scheduled(cls) -> list[Post]:
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
            scheduled = [Post(**item) for item in execute['items']]
        except:
            scheduled = []

        return scheduled

    @classmethod
    def get_scheduled_as_list(cls) -> list[list[str]]:
        # Quiero una lista de listas.
        ans: list[list[str]] = []
        # Cada sublista deberá tener 4 elementos:
        # título, link(vacío), director y año
        scheduled = cls.get_scheduled()

        for post in scheduled:
            # Parseo el contenido
            body = BeautifulSoup(post.content, 'html.parser')

            # Extraigo los datos que quiero
            director = BlogHiddenData.DIRECTOR.get(body)
            year = BlogHiddenData.YEAR.get(body)
            title = BlogHiddenData.TITLE.get(body)

            ans.append([title, "", director, year])

        return ans


def date_to_str(date: date | datetime, *,
                TIME_ZONE=tz.gettz('Europe/Madrid')) -> str:
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
