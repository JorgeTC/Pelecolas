from datetime import date, datetime, timedelta, time
from typing import Iterable

from dateutil import tz
from oauth2client import client

from src.config import Config, Param, Section

from ..aux_title_str import DMY, date_from_DMY, date_from_YMD, time_from_str
from . import blog_client as Client
from .api_dataclasses import Post
from .blog_client import PostStatus


class Poster:

    # Guardo el primer mes que tiene reseña
    __first_month = date(2019, 1, 1)

    @classmethod
    def add_post(cls, content: str, title: str, labels: str):

        # Cuándo se va a publicar la reseña
        str_date = get_publish_datatime()

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
            Client.insert_post(body, bDraft)
        except client.AccessTokenRefreshError:
            print('The credentials have been revoked or expired, please re-run'
                  'the application to re-authorize')
            return
        # Si no está programada como borrador, aviso al usuario de cuándo se va a publicar la reseña
        if not bDraft:
            print(f"La reseña de {title} "
                  f"se publicará el {DMY(str_date[:10])}")

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
        Client.update_post(new_post)

    @classmethod
    def delete_post(cls, post: Post):
        Client.delete_post(post)

    @classmethod
    def get_published_from_date(cls, min_date: date | datetime) -> list[Post]:

        # Las fechas deben estar introducidas en formato date
        # Las convierto a cadena
        min_date = date_to_str(min_date)

        # Pido los blogs desde entonces
        return list(iter_posts(min_date, PostStatus.LIVE))

    @classmethod
    def get_draft_from_date(cls, min_date: date | datetime) -> list[Post]:

        # Las fechas deben estar introducidas en formato date
        # Las convierto a cadena
        min_date = date_to_str(min_date)

        # Pido los blogs desde entonces
        return list(iter_posts(min_date, PostStatus.DRAFT))

    @classmethod
    def get_scheduled(cls) -> list[Post]:
        # Hago una lista de todos los posts programados a partir de hoy
        today = datetime.today()
        start_date = date_to_str(today)

        return list(iter_posts(start_date, PostStatus.SCHEDULED))


def iter_posts(start_date: str, post_status: PostStatus) -> Iterable[Post]:
    # Token para poder hacer varias peticiones
    page_token: str | None = None
    while True:
        # Pido los archivos que tengan como carpeta parent la que he introducido
        posts, page_token = Client.list_posts(start_date, post_status,
                                              page_token)

        # Itero lo que me ha dado la api en esta petición
        for post in posts:
            yield Post(**post)
        # Avanzo a la siguiente petición
        if page_token is None:
            return


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
    except Exception:
        raise ValueError


def get_automatic_date(post_time: time) -> date:

    scheduled = Poster.get_scheduled()

    # Extraigo todas las fechas que ya tienen asignado un blog
    dates = {str(date_from_YMD(post.published)) for post in scheduled}

    # Busco los viernes disponibles
    # Voy al próximo viernes
    today = datetime.today().date()
    week_day = today.weekday()
    days_till_next_friday = (4 - week_day) % 7
    if days_till_next_friday == 0:
        if datetime.today().time() < post_time:
            days_till_next_friday = 7
    next_friday = today + timedelta(days=days_till_next_friday)

    # Avanzo por los viernes hasta encontrar uno que esté disponible
    while (str_next_friday := str(next_friday)) in dates:
        # Avanzo al siguiente viernes
        next_friday = next_friday + timedelta(days=7)

    # Devuelvo la fecha encontrada como fecha
    return date_from_YMD(str_next_friday)


def get_publish_datatime() -> str:
    # Obtengo a qué hora tengo que publicar la reseña
    sz_time = Config.get_value(Section.POST, Param.TIME)
    time = time_from_str(sz_time)

    # Obtengo qué día tengo que publicar la reseña
    sz_date = Config.get_value(Section.POST, Param.DATE)
    try:
        publish_date = date_from_DMY(sz_date)
    except ValueError:
        # Si no consigo interpretarlo como fecha, le doy la fecha automática
        publish_date = get_automatic_date(time)

    return date_to_str(datetime.combine(publish_date, time))
