from googleapiclient.discovery import Resource
from googleapiclient.http import MediaFileUpload

from src.api_dataclasses import DriveFile
from src.config import Config, Param, Section
from src.google_api_mgr import GetGoogleApiMgr

TYPE_FOLDER = 'application/vnd.google-apps.folder'


class Drive():

    SERVICE: Resource = GetGoogleApiMgr('drive')

    def __init__(self) -> None:

        # Gestor de archivos en el drive
        self.files: Resource = self.SERVICE.files()

        # Obtengo la carpeta dentro del drive
        self.folder_id = Config.get_value(Section.DRIVE, Param.FOLDER_ID)
        self.folder = self.get_item_by_id(self.folder_id)

        # Obtengo la carpeta donde vive el pdf
        self.pdf_folder = Config.get_folder_path(
            Section.DRIVE, Param.PDF_PATH)
        # Obtengo la carpeta donde viven los docx
        self.docx_folder = Config.get_folder_path(
            Section.COUNT_FILMS, Param.WORD_FOLDER)

    def update_folder(self):
        # Obtengo los archivos dentro de la carpeta
        files_in_folder = self.get_files_in_folder(self.folder_id)
        # Le paso todos los archivos para actualizar
        self.update_files(files_in_folder)

    def update_files(self, files_to_update: list[DriveFile]):
        # Itero los archivos de la lista
        for file in files_to_update:

            # Contenido del nuevo archivo
            if file.name.find('.docx') >= 0:
                # Caso en el que sea un word
                sz_file = self.docx_folder / file.name
            else:
                # Caso en el que sea el pdf
                sz_file = self.pdf_folder / file.name

            # Realizo la actualización
            # Obtengo el archivo como un objeto
            media_body = MediaFileUpload(sz_file, resumable=True)
            # Defino la acción de actualización
            update_operation = self.files.update(
                fileId=file.id,
                media_body=media_body)
            # Ejecuto la actualización
            update_operation.execute()

    def get_item_by_id(self, sz_id: str):
        try:
            return self.files.get(fileId=sz_id).execute()
        except:
            return None

    def get_files_in_folder(self, sz_folder_id: str) -> list[DriveFile]:

        answer = []

        # Índice para iterar las peticiones a la api
        page_token = None
        while True:
            # Pido los archivos que tengan como carpeta parent la que he introducido
            response = self.files.list(q=f"'{sz_folder_id}' in parents",
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
