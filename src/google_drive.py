from googleapiclient.http import MediaFileUpload

from src.dlg_config import CONFIG
from src.google_api_mgr import GoogleApiMgr

TYPE_FOLDER = 'application/vnd.google-apps.folder'


class Drive(GoogleApiMgr):

    def __init__(self, sz_folder) -> None:
        GoogleApiMgr.__init__(self, 'drive')

        # Gestor de archivos en el drive
        self.files = self.SERVICE.files()

        # Obtengo la carpeta dentro del drive
        self.folder_id = CONFIG.get_value(CONFIG.S_DRIVE, CONFIG.P_FOLDER_ID)
        self.folder = self.get_item_by_id(self.folder_id)

        # Obtengo la carpeta donde vive el pdf
        self.pdf_folder = sz_folder
        # Obtengo la carpeta donde viven los docx
        self.docx_folder = sz_folder / \
            CONFIG.get_value(CONFIG.S_COUNT_FILMS, CONFIG.P_WORD_FOLDER)

    def update_folder(self):
        # Obtengo los archivos dentro de la carpeta
        files_in_folder = self.get_files_in_folder(self.folder_id)
        # Le paso todos los archivos para actualizar
        self.update_files(files_in_folder)

    def update_files(self, files_to_update):
        # Itero los archivos de la lista
        for file in files_to_update:

            # Contenido del nuevo archivo
            if file['name'].find('.docx') >= 0:
                # Caso en el que sea un word
                sz_file = self.docx_folder / file['name']
            else:
                # Caso en el que sea el pdf
                sz_file = self.pdf_folder / file['name']

            # Realizo la actualización
            # Obtengo el archivo como un objeto
            media_body = MediaFileUpload(sz_file, resumable=True)
            # Defino la acción de actualización
            update_operation = self.files.update(
                fileId=file['id'],
                media_body=media_body)
            # Ejecuto la actualización
            update_operation.execute()

    def get_item_by_id(self, sz_id):
        try:
            return self.files.get(fileId=sz_id).execute()
        except:
            return None

    def get_files_in_folder(self, sz_folder_id):

        answer = []
        try:
            # Índice para iterar las peticiones a la api
            page_token = None
            while True:
                # Pido los archivos que tengan como carpeta parent la que he introducido
                response = self.files.list(q="'{}' in parents".format(sz_folder_id),
                                           spaces='drive',
                                           fields='nextPageToken, files(id, name, trashed)',
                                           pageToken=page_token).execute()

                # Itero lo que me ha dado la api en esta petición
                for file in response.get('files', []):
                    # Compruebo que sean archivos no eliminados
                    if not file['trashed']:
                        answer.append(file)

                # Avanzo a la siguiente petición
                page_token = response.get('nextPageToken', None)

                # Si no puedo hacer más peticiones, salgo del bucle
                if page_token is None:
                    break

            # Devuelo la lista
            return answer
        except:
            # Si algo ha ido mal, devuelvo una lista vacía
            return []
