from googleapiclient import sample_tools
from oauth2client import client

class Poster():
    SERVICE, _ = sample_tools.init(
        [__file__], 'blogger', 'v3', __doc__, __file__,
        scope='https://www.googleapis.com/auth/blogger')

    BLOG_ID = '4259058779347983900'

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

        # Creo el contenido que voy a publicar
        body = {
            "kind": "blogger#post",
            "title": title,
            "content": content
        }

        try:
            # Añado el post como borrador
            self.posts.insert(blogId=self.BLOG_ID, body=body, isDraft=True).execute()
        except client.AccessTokenRefreshError:
            print ('The credentials have been revoked or expired, please re-run'
                'the application to re-authorize')
