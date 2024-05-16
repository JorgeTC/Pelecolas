from enum import StrEnum
from pathlib import Path
from threading import Lock
from typing import Iterable

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import Resource, build

from src.aux_res_directory import get_res_folder

# Dirección del archivo con las credenciales del blog
CREDENTIALS_PATH = get_res_folder("blog_credentials", "client_secrets.json")
# Dirección del archivo con el token de acceso
TOKEN_PATH = get_res_folder("blog_credentials", "token.json")


refreshing_lock = Lock()


def refreshed_credentials(creds: Credentials | None, credentials_path: Path, token_path: Path, scopes: Iterable[str]) -> Credentials:
    # Si las credenciales ya son válidas, las devuelvo
    if creds and creds.valid:
        return creds

    # Si las puedo refrescar, lo hago
    try:
        creds.refresh(Request())
    # No puedo refrescar, debo generarlo de nuevo
    except Exception:
        flow = InstalledAppFlow.from_client_secrets_file(credentials_path,
                                                         scopes)
        creds = flow.run_local_server(port=0,
                                      authorization_prompt_message="Abriendo navegador para autorizar la app.",
                                      success_message="Autorización completada con éxito.")

    # Actualizo el archivo con el token de acceso
    with open(token_path, 'w') as token:
        token.write(creds.to_json())

    return creds


def get_credentials(credentials_path: Path, token_path: Path, scopes: Iterable[str]) -> Credentials:
    # Si existe el archivo, puedo generar credenciales
    creds = (Credentials.from_authorized_user_file(token_path, scopes)
             if token_path.is_file() else None)

    # No he obtenido credenciales válidas
    with refreshing_lock:
        creds = refreshed_credentials(creds, credentials_path,
                                      token_path, scopes)

    return creds


class GoogleService(StrEnum):
    BLOGGER = 'blogger'
    DRIVE = 'drive'


def get_google_service(api_type: GoogleService,
                       credentials_path=CREDENTIALS_PATH, token_path=TOKEN_PATH) -> Resource:
    # Defino los servicios de Google que voy a manejar
    SCOPES = tuple(f"https://www.googleapis.com/auth/{service}"
                   for service in GoogleService)

    credentials = get_credentials(credentials_path, token_path, SCOPES)

    return build(api_type, 'v3', credentials=credentials)
