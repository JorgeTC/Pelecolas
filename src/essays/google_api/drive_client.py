from functools import cache

from googleapiclient.discovery import HttpRequest, Resource
from googleapiclient.http import MediaFileUpload

from .google_api_mgr import get_google_service, GoogleService
from .google_client import GoogleClient


@cache
def SERVICE() -> Resource:
    return get_google_service(GoogleService.DRIVE)


@cache
def FILES() -> Resource:
    return SERVICE().files()


def update_file(file_id: str, media_body: MediaFileUpload) -> None:
    # Defino la acción de actualización
    update_operation: HttpRequest = FILES().update(fileId=file_id,
                                                   media_body=media_body)
    GoogleClient.execute(update_operation)


def get_item(item_id: str):
    get_operation: HttpRequest = FILES().get(fileId=item_id)

    return GoogleClient.execute_and_wait(get_operation)


def list_files(folder_id: str, page_token: str | None) -> tuple[list[dict[str, str | bool]], str | None]:
    list_operation: HttpRequest = FILES().list(q=f"'{folder_id}' in parents",
                                               spaces='drive',
                                               fields='nextPageToken, files(id, name, trashed)',
                                               pageToken=page_token)

    response: dict = GoogleClient.execute_and_wait(list_operation)

    files_list = response.get('files', [])
    next_page_token = response.get('nextPageToken', None)

    return files_list, next_page_token
