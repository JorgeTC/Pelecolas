from pathlib import Path
from typing import Iterable

from googleapiclient.http import MediaFileUpload

from src.config import Config, Param, Section

from . import drive_client as Client
from .api_dataclasses import DriveFile
from .thread_safe_property import thread_safe_cache

TYPE_FOLDER = 'application/vnd.google-apps.folder'


class Drive:

    # Obtengo la carpeta dentro del drive
    FOLDER_ID = Config.get_value(Section.DRIVE, Param.FOLDER_ID)

    @classmethod
    def update_folder(cls):
        # Le paso todos los archivos para actualizar
        cls.update_files(cls.FILES_IN_DRIVE())

    @classmethod
    def update_docx_files(cls):
        docx_files = [path for path in cls.FILES_IN_DRIVE()
                      if '.docx' in path.name]
        cls.update_files(docx_files)

    @classmethod
    def update_pdf_files(cls):
        pdf_files = [path for path in cls.FILES_IN_DRIVE()
                     if '.pdf' in path.name]
        cls.update_files(pdf_files)

    @classmethod
    def update_files(cls, files_to_update: list[DriveFile]):
        # Itero los archivos de la lista
        for file in files_to_update:
            file_path = get_path_from_drive_file(file)

            # Realizo la actualización
            # Obtengo el archivo como un objeto
            media_body = MediaFileUpload(file_path, resumable=True)
            # Defino la acción de actualización
            Client.update_file(file.id, media_body)

    @classmethod
    @thread_safe_cache
    def FILES_IN_DRIVE(cls) -> list[DriveFile]:
        # Lista de todos los archivos que están subidos a Google Drive
        return cls.get_files_in_folder(cls.FOLDER_ID)

    @classmethod
    def get_item_by_id(cls, sz_id: str):
        return Client.get_item(sz_id)

    @classmethod
    def get_files_in_folder(cls, sz_folder_id: str) -> list[DriveFile]:
        # Devuelvo una lista con todos los archivos no eliminados
        # en la carpeta introducida
        return [file
                for file in iter_folder(sz_folder_id)
                if not file.trashed]


def iter_folder(folder_id: str) -> Iterable[DriveFile]:
    # Token para poder hacer varias peticiones
    page_token: str | None = None
    while True:
        # Pido los archivos que tengan como carpeta parent la que he introducido
        files, page_token = Client.list_files(folder_id, page_token)

        # Itero lo que me ha dado la api en esta petición
        for file in files:
            yield DriveFile(**file)
        # Avanzo a la siguiente petición
        if page_token is None:
            return


def get_path_from_drive_file(file: DriveFile, *,
                             PDF_FOLDER=Config.get_folder_path(
                                 Section.DRIVE, Param.PDF_PATH),
                             DOCX_FOLDER=Config.get_folder_path(
                                 Section.COUNT_FILMS, Param.WORD_FOLDER)) -> Path:

    if '.docx' in file.name:
        # Caso en el que sea un word
        return DOCX_FOLDER / file.name
    elif '.pdf' in file.name:
        # Caso en el que sea el pdf
        return PDF_FOLDER / file.name

    return Path()
