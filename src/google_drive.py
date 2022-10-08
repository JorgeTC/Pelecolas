from pathlib import Path
from googleapiclient.discovery import Resource
from googleapiclient.http import MediaFileUpload

from src.api_dataclasses import DriveFile
from src.config import Config, Param, Section
from src.google_api_mgr import GetGoogleApiMgr

TYPE_FOLDER = 'application/vnd.google-apps.folder'


class Drive():

    # Google Drive API
    _SERVICE: Resource = None
    # Gestor de archivos de Drive
    _FILES: Resource = None

    # Obtengo la carpeta dentro del drive
    FOLDER_ID = Config.get_value(Section.DRIVE, Param.FOLDER_ID)

    # Lista de todos los archivos que están subidos a Google Drive
    _FILES_IN_DRIVE: list[DriveFile] = None

    @classmethod
    def update_folder(cls):
        # Le paso todos los archivos para actualizar
        cls.update_files(cls.FILES_IN_DRIVE)

    @classmethod
    def update_docx_files(cls):
        docx_files = [path for path in cls.FILES_IN_DRIVE
                      if path.name.find('.docx') >= 0]
        cls.update_files(docx_files)

    @classmethod
    def update_pdf_files(cls):
        pdf_files = [path for path in cls.FILES_IN_DRIVE
                     if path.name.find('.pdf') >= 0]
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
            update_operation = cls.FILES.update(
                fileId=file.id,
                media_body=media_body)
            # Ejecuto la actualización
            update_operation.execute()

    @classmethod
    @property
    def FILES_IN_DRIVE(cls) -> list[DriveFile]:
        if cls._FILES_IN_DRIVE is None:
            cls._FILES_IN_DRIVE = cls.get_files_in_folder(cls.FOLDER_ID)
        return cls._FILES_IN_DRIVE

    @classmethod
    @property
    def SERVICE(cls) -> Resource:
        if cls._SERVICE is None:
            cls._SERVICE = GetGoogleApiMgr('drive')
        return cls._SERVICE

    @classmethod
    @property
    def FILES(cls) -> Resource:
        if cls._FILES is None:
            cls._FILES = cls.SERVICE.files()
        return cls._FILES

    @classmethod
    def get_item_by_id(cls, sz_id: str):
        try:
            return cls.FILES.get(fileId=sz_id).execute()
        except:
            return None

    @classmethod
    def get_files_in_folder(cls, sz_folder_id: str) -> list[DriveFile]:

        answer = []

        # Índice para iterar las peticiones a la api
        page_token = None
        while True:
            # Pido los archivos que tengan como carpeta parent la que he introducido
            response = cls.FILES.list(q=f"'{sz_folder_id}' in parents",
                                      spaces='drive',
                                      fields='nextPageToken, files(id, name, trashed)',
                                      pageToken=page_token).execute()

            # Itero lo que me ha dado la api en esta petición
            for file in response.get('files', []):
                drive_file = DriveFile(**file)
                # Compruebo que sean archivos no eliminados
                if not drive_file.trashed:
                    answer.append(drive_file)

            # Avanzo a la siguiente petición
            page_token = response.get('nextPageToken', None)

            # Si no puedo hacer más peticiones, salgo del bucle
            if page_token is None:
                break

        # Devuelvo la lista
        return answer


def get_path_from_drive_file(file: DriveFile, *,
                             PDF_FOLDER=Config.get_folder_path(
                                 Section.DRIVE, Param.PDF_PATH),
                             DOCX_FOLDER=Config.get_folder_path(
                                 Section.COUNT_FILMS, Param.WORD_FOLDER)) -> Path:

    if file.name.find('.docx') >= 0:
        # Caso en el que sea un word
        return DOCX_FOLDER / file.name
    elif file.name.find('.pdf') >= 0:
        # Caso en el que sea el pdf
        return PDF_FOLDER / file.name

    return Path()
