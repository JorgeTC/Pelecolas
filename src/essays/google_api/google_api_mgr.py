from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import Resource, build

from src.aux_res_directory import get_res_folder

# Dirección del archivo con las credenciales del blog
CREDENTIALS_PATH = get_res_folder("blog_credentials", "client_secrets.json")
# Dirección del archivo con el token de acceso
TOKEN_PATH = get_res_folder("blog_credentials", "token.json")


def get_credentials() -> Credentials:
    # Defino los servicios de Google que voy a manejar
    SCOPES = tuple(f"https://www.googleapis.com/auth/{service}"
                   for service in ('blogger', 'drive'))

    # Si existe el archivo, puedo generar credenciales
    creds = (Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)
             if TOKEN_PATH.is_file() else None)

    # No he obtenido credenciales válidas
    if not creds or not creds.valid:
        # Si las puedo refrescar, lo hago
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        # No puedo refrescar, debo generarlo de nuevo
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                CREDENTIALS_PATH, SCOPES)
            creds = flow.run_local_server(port=0)

        # Actualizo el archivo con el token de acceso
        with open(TOKEN_PATH, 'w') as token:
            token.write(creds.to_json())

    return creds


def get_google_service(api_type: str) -> Resource:
    return build(api_type, 'v3', credentials=get_credentials())
