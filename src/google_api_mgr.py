from googleapiclient import sample_tools
from googleapiclient.discovery import Resource

from src.aux_res_directory import get_res_folder

# Dirección del archivo con las credenciales del blog
SZ_CREDENTIALS = get_res_folder("blog_credentials", "client_secrets.json")


def GetGoogleApiMgr(type: str) -> Resource:
    SERVICE, _ = sample_tools.init(
        [__file__], type, 'v3', __doc__, SZ_CREDENTIALS,
        scope=f'https://www.googleapis.com/auth/{type}')

    return SERVICE
