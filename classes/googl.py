import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload


class GooClient:
    """
    класс для google-api, создается по токену, scopes, имени папки

    методы:
    load_file(path, name) принимает путь к файлу на компьютере и имя,
    под которым его нужно сохранить
    возвращает True, если успешно загрузит файл в папку на google.drive

    get_list_files() возвращает список файлов, можно передать аргумент q="запрос"
        """
    def __init__(self, token, scopes, fold_name):
        creds = None
        if os.path.exists(token):
            creds = Credentials.from_authorized_user_file(token, scopes)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    "classes/secret/credentials.json", scopes
                )
                creds = flow.run_local_server(port=0)
        self._creds = creds
        self.fold_id = self._create_folder(fold_name)
        # Save the credentials for the next run
        with open(token, "w") as key:
            key.write(creds.to_json())

    def get_list_files(self, q="trashed=false"):
        try:
            service = build("drive", "v3", credentials=self._creds)
            resp = (
                service.files()
                .list(pageSize=10, q=q, fields="nextPageToken, files(id, name)")
                .execute()
            )
            items = resp.get("files", [])
            return items
        except HttpError as error:
            print(f"An error occurred: {error}")

    def _create_folder(self, name):
        q = "mimeType = 'application/vnd.google-apps.folder' and trashed=false"
        self.folders = {item["name"]: item["id"] for item in
                        self.get_list_files(q=q)}
        if name in self.folders:
            return self.folders[name]
        try:
            service = build("drive", "v3", credentials=self._creds)
            file_metadata = {
                "name": name,
                "mimeType": "application/vnd.google-apps.folder",
            }
            file = service.files().create(body=file_metadata, fields="id").execute()
            return file.get("id")

        except HttpError as error:
            print(f"An error occurred: {error}")
            return None

    def load_file(self, path, name):
        try:
            service = build("drive", "v3", credentials=self._creds)
            file_metadata = {"name": name, "parents": [self.fold_id]}
            media = MediaFileUpload(path, mimetype="image/jpg", resumable=True)
            file = (
                service.files()
                .create(body=file_metadata, media_body=media, fields="id")
                .execute()
            )
        except HttpError as error:
            print(f"An error occurred: {error}")
            file = None
        return file.get("id")

