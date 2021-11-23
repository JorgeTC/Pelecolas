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

        except client.AccessTokenRefreshError:
            print ('The credentials have been revoked or expired, please re-run'
                'the application to re-authorize')

    def add_post(self, content, title):

        # Compruebo que el blog que tengo guardado sea el correcto
        if self.blog['id'] != self.BLOG_ID:
            return False

        time_zone = pytz.timezone('CET')
        str_date = datetime(2025,11,23,21,51, tzinfo=time_zone).isoformat()
        # Creo el contenido que voy a publicar
        body = {
            "kind": "blogger#post",
            "title": title,
            "content": content,
            "labels": "a,b,c",
            "published": str_date
        }

        try:
            # Añado el post como borrador
            f = self.posts.insert(blogId=self.BLOG_ID, body=body, isDraft=False)
            f.execute()

        except client.AccessTokenRefreshError:
            print ('The credentials have been revoked or expired, please re-run'
                'the application to re-authorize')
