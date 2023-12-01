import requests
from datetime import datetime


class Vkclient:
    """
    класс для vk-api, создается по токену и id

    атрибуты:
    albums - словарь, где ключи - имена непустых альбомов, а значения - их id

    методы:
    get_photo(self, album) принимает id альбома(необязательно), возвращает генератор фото в нем.
    без аргументов фото будут из профиля
    """
    def _build_url(self, method):
        return f"https://api.vk.com/method/{method}"

    def _get_params(self):
        return {"access_token": self.token,
                "v": "8.56.1"}

    def _is_ok(self, resp):
        if "error" in resp.json():
            print(resp.json()["error"]["error_msg"])
            return False
        return 200 <= resp.status_code < 300

    def __init__(self, token, user_id):
        self.token = token
        self.user_id = user_id
        self.albums = self._get_albums()
        self.files = set()

    def _get_albums(self):
        params = self._get_params()
        params.update(({"owner_id": self.user_id}))
        resp = requests.get(self._build_url("photos.getAlbums"), params=params)
        if self._is_ok(resp):
            return {album.get("title"): album.get("id")
                    for album in resp.json()["response"].get("items")
                    if album["size"] > 0}
        return {}

    def get_photo(self, album="profile"):
        params = self._get_params()
        params.update(({"owner_id": self.user_id, "album_id": album, "extended": "true"}))
        resp = requests.get(self._build_url("photos.get"), params=params)
        photos = []
        if not self._is_ok(resp):
            return []
        for item in resp.json()["response"].get("items"):
            url = item["sizes"][-1]["url"]
            size = item["sizes"][-1]["type"]
            likes = str(item["likes"]["count"])
            date = item["date"]
            if not likes in self.files:
                name = likes
            else:
                name = f'{likes}-{str(datetime.fromtimestamp(date)).replace(" ", "_").replace(":", "_")}'
            self.files.add(name)
            yield {"size": size, "name": name+".jpg", "url": url}
