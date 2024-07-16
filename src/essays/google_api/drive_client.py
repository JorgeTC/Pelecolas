from functools import cache

from googleapiclient.discovery import HttpRequest, Resource
from googleapiclient.http import MediaFileUpload

from ..async_initializer import AsyncInitializer
from .google_api_mgr import GoogleService, get_google_service
from .google_client import GoogleClient


def get_drive_service():
    return get_google_service(GoogleService.DRIVE)


DRIVE_SERVICE = AsyncInitializer(get_drive_service)


def get_files():
    drive_service = DRIVE_SERVICE.get()
    return drive_service.files()


FILES = AsyncInitializer(get_files)


def update_file(file_id: str, media_body: MediaFileUpload) -> None:
    # Defino la acción de actualización
    files = FILES.get()
    update_operation: HttpRequest = files.update(fileId=file_id,
                                                 media_body=media_body)
    GoogleClient.execute(update_operation)


def get_item(item_id: str):
    files = FILES.get()
    get_operation: HttpRequest = files.get(fileId=item_id)

    return GoogleClient.execute_and_wait(get_operation)


def list_files(folder_id: str, page_token: str | None) -> tuple[list[dict[str, str | bool]], str | None]:
    files = FILES.get()
    list_operation: HttpRequest = files.list(q=f"'{folder_id}' in parents",
                                             spaces='drive',
                                             fields='nextPageToken, files(id, name, trashed)',
                                             pageToken=page_token)

    response: dict = GoogleClient.execute_and_wait(list_operation)

    files_list = response.get('files', [])
    next_page_token = response.get('nextPageToken', None)

    return files_list, next_page_token
