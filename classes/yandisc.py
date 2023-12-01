import requests


class Yandisc:
    """
    класс для yandex-api, создается по токену

    атрибуты:
    folder(по умолчанию vk-backup) можно указать при создании экземпляра
    *такой папки не должно существовать на диске

    функции:
    load_photo(self, photo) принимает словарь с инфо о файле,
    где должны быть ключи 'name', 'url'
    возвращает True, если успешно загрузит файл в папку на яндекс.диск
    """
    def __init__(self, token, folder="vk-backup"):
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
        params = {"path": folder}
        if self._is_ok(requests.put(self.base_url,
                            headers=self.headers,
                            params=params)):
            return folder

    def load_photo(self, photo):
        path = f'{self.folder}/{photo["name"]}'
        resp = requests.get(photo["url"])
        if not self._is_ok(resp):
            return
        file = resp.content
        url = self._get_url(path)
        return requests.put(url, files={"file": file}).status_code == 201
