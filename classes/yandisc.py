import requests


class Yandisc:
    """
    класс для yandex-api, создается по токену и имени папки

    функции:
    load_photo(self, photo) принимает словарь с инфо о файле,
    где должны быть ключи 'name', 'url'
    возвращает True, если успешно загрузит файл в папку на яндекс.диск
    """
    def __init__(self, token, folder):
        self.token = token
        self.headers = {
            "Authorization": "OAuth "+token
        }
        self.base_url = "https://cloud-api.yandex.net/v1/disk/resources/"
        self.folder = self._add_folder(folder)

    def _is_ok(self, resp):
        return 200 <= resp.status_code < 300

    def _get_url(self, name):
        params = {"path": name}
        resp = requests.get(self.base_url+"upload",
                            headers=self.headers,
                            params=params)
        return resp.json().get("href", "")

    def _add_folder(self, folder):
        if folder in self._get_folders_list():
            return folder
        params = {"path": folder}
        if self._is_ok(requests.put(self.base_url,
                            headers=self.headers,
                            params=params)):
            return folder

    def _get_folders_list(self):
        params = {"path": '/',
                  "fields": ["_embedded.items.name"]}
        resp = requests.get(self.base_url[:-1], params=params, headers=self.headers)
        if self._is_ok(resp):
            return [folder["name"] for folder in resp.json()["_embedded"]["items"]]

    def _get_files_list(self):
        params = {"path": f'{self.folder}',
                  "fields": ["_embedded.items.name"]}
        resp = requests.get(self.base_url, params=params, headers=self.headers)
        if self._is_ok(resp):
            return [file["name"] for file in resp.json()["_embedded"]["items"]]

    def load_photo(self, photo):
        if photo["name"] in self._get_files_list():
            print(f"В папке {self.folder} уже есть файл {photo['name']}")
            return False
        path = f'{self.folder}/{photo["name"]}'
        resp = requests.get(photo["url"])
        if not self._is_ok(resp):
            print("error get photo")
        file = resp.content
        url = self._get_url(path)
        return requests.put(url, files={"file": file}).status_code == 201
