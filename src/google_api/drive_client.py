from googleapiclient.discovery import HttpRequest, Resource
from googleapiclient.http import MediaFileUpload

from src.google_api.google_api_mgr import get_google_service
from src.google_api.google_client import GoogleClient

from .thread_safe_property import thread_safe_cache


@thread_safe_cache
def SERVICE() -> Resource:
    return get_google_service('drive')


@thread_safe_cache
def FILES() -> Resource:
    return SERVICE().files()


def update_file(file_id: str, media_body: MediaFileUpload) -> None:
    # Defino la acción de actualización
    update_operation: HttpRequest = FILES().update(
        fileId=file_id,
        media_body=media_body)
    GoogleClient.execute(update_operation)


def get_item(item_id: str):
    get_operation: HttpRequest = FILES().get(fileId=item_id)

    return GoogleClient.execute_and_wait(get_operation)


def list_files(folder_id: str, page_token: str) -> tuple[list[dict[str, str | bool]], str]:
    list_operation: HttpRequest = FILES().list(q=f"'{folder_id}' in parents",
                                               spaces='drive',
                                               fields='nextPageToken, files(id, name, trashed)',
                                               pageToken=page_token)

    response: dict = GoogleClient.execute_and_wait(list_operation)

    files_list = response.get('files', [])
    next_page_token = response.get('nextPageToken', None)

    return files_list, next_page_token
