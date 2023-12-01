from classes.yandisc import Yandisc
from classes.vk_client import Vkclient
from environs import Env
import requests
import logging
from classes.googl import GooClient
from tqdm import tqdm

logging.basicConfig(level=logging.INFO, filename="temp/log.log", filemode="w",
                    format="%(asctime)s %(levelname)s %(message)s")


def get_config():
    env = Env()
    env.read_env()
    conf = {
        "ya_token": env("OATH_TOKEN"),
        "vk_token": env("VK_TOKEN"),
        "vk_id": env("VK_ID"),
        "scopes" : ["https://www.googleapis.com/auth/drive.file"],
        "path_gtoken": "classes/secret/google_token.json"
    }
    return conf


def get_vk_photos(vk_client: Vkclient, count=5, album=None):
    """
    принимает обьект класса Vkclient, и необязательные параметры - количество фото и id альбома
    возвращает список словарей с ключами 'url', 'name', 'size'(максимальный размер)
    """
    source = vk_client.get_photo(album) if album else vk_client.get_photo()
    photos = []
    for i in range(count):
        try:
            photos.append(next(source))
        except StopIteration:
            logging.info("Not more photos in album")
            break
        else:
            logging.info(f"Data about photo {photos[-1]['name']} received from vk")
    return photos


def ya_load(ya_client: Yandisc, files: [dict]):
    for file in tqdm(files, colour="green"):
        if ya_client.load_photo(file):
            logging.info(f"File {file['name']} load to Yandex.Disc OK")
        else:
            logging.error(f"File {file['name']} load error")



def go_load(client: GooClient, files: [dict]):
    for file in tqdm(files, colour="blue"):
        resp = requests.get(file["url"])
        with open("temp/file.jpg", "wb") as f:
            f.write(resp.content)
        if (res := client.load_file("temp/file.jpg", file["name"])):
            logging.info(f"{file['name']} load to Google.Drive OK, file_id: {res}")


if __name__ == "__main__":
    conf = get_config()
    vk_client = Vkclient(conf["vk_token"], conf["vk_id"])
    ya_loader = Yandisc(conf["ya_token"])
    go_loader = GooClient(conf["path_gtoken"], conf["scopes"])
    for alb in vk_client.albums:
        files_dicts = get_vk_photos(vk_client, 5, alb["id"])
        ya_load(ya_loader, files_dicts)
        go_load(go_loader, files_dicts)

