from src.aux_res_directory import get_res_folder
from googleapiclient import sample_tools

class GoogleApiMgr():
    # Dirección del archivo con las credenciales del blog
    sz_credentials = get_res_folder("blog_credentials", "client_secrets.json")

    def __init__(self, sz_type):
        self.SERVICE, _ = sample_tools.init(
            [__file__], sz_type, 'v3', __doc__, self.sz_credentials,
            scope='https://www.googleapis.com/auth/{}'.format(sz_type))

    def get_service(self):
        return self.SERVICE
