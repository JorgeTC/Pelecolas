from datetime import datetime
import pytz
from googleapiclient import sample_tools
from oauth2client import client
from dlg_config import CONFIG

class Poster():
    SERVICE, _ = sample_tools.init(
        [__file__], 'blogger', 'v3', __doc__, __file__,
        scope='https://www.googleapis.com/auth/blogger')

    BLOG_ID = CONFIG.get_value(CONFIG.S_POST, CONFIG.P_BLOG_ID)

    def __init__(self):
        try:
            users = self.SERVICE.users()

            # Retrieve this user's profile information
            self.thisuser = users.get(userId='self').execute()

            blogs = self.SERVICE.blogs()

            # Retrieve the list of Blogs this user has write privileges on
            thisusersblogs = blogs.listByUser(userId='self').execute()

            self.posts = self.SERVICE.posts()

            self.blog = thisusersblogs['items'][0]
            for blog in thisusersblogs['items']:
                if blog['id'] == self.BLOG_ID:
                    self.blog = blog

        except client.AccessTokenRefreshError:
            print ('The credentials have been revoked or expired, please re-run'
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
            f = self.posts.insert(blogId=self.BLOG_ID, body=body, isDraft=bDraft)
            f.execute()

        except client.AccessTokenRefreshError:
            print ('The credentials have been revoked or expired, please re-run'
                'the application to re-authorize')

    def __get_publish_datatime(self):
        # Obtengo qué día tengo que publicar la reseña
        sz_date = CONFIG.get_value(CONFIG.S_POST, CONFIG.P_DATE)
        if sz_date.lower() == 'auto':
            self.__get_automatic_date()
            pass
        else:
            sz_date = sz_date.split("/")
            sz_day = int(sz_date[0])
            sz_month = int(sz_date[1])
            sz_year = int(sz_date[2])
        # Obtengo a qué hora tengo que publicar la reseña
        sz_time = CONFIG.get_value(CONFIG.S_POST, CONFIG.P_TIME)
        sz_hour = int(sz_time.split(":")[0])
        sz_minute = int(sz_time.split(":")[1])

        return datetime(sz_year, sz_month, sz_day,
                        sz_hour,sz_minute,
                        tzinfo=pytz.UTC).isoformat()

    def __get_automatic_date(self):

        today = datetime.today().date()

        today = datetime(today.year, today.month, today.day,
                        tzinfo=pytz.UTC).isoformat()

        ls = self.posts.list(blogId=self.BLOG_ID,
                             maxResults = 50,
                             startDate = today)
