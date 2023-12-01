from environs import Env
import logging
import requests

from tqdm import tqdm

from classes.googl import GooClient
from classes.yandisc import Yandisc
from classes.vk_client import Vkclient


logging.basicConfig(level=logging.INFO, filename="temp/log.log", filemode="w",
                    format="%(asctime)s %(levelname)s %(message)s")


def get_config():
    env = Env()
    env.read_env()
    conf = {
        "ya_token": env("OATH_TOKEN"),
        "vk_token": env("VK_TOKEN"),
        "vk_id": env("VK_ID"),
        "scopes": ["https://www.googleapis.com/auth/drive.file"],
        "path_gtoken": "classes/secret/google_token.json"
    }
    return conf


def get_vk_photos(vk_client: Vkclient, album, count):
    """
    принимает обьект класса Vkclient, и параметры - id альбома, количество фото
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
        else:
            logging.error(f"{file['name']} load to Google failed ")


if __name__ == "__main__":
    conf = get_config()
    name = input("Введите имя папки, или пропустите этот шаг (по умолчанию будет названа 'vk-backup')\n")
    conf["name"] = name or "vk-backup"
    vk_client = Vkclient(conf["vk_token"], conf["vk_id"])
    alb_list = [(i, v) for i, v in enumerate(vk_client.albums.keys())]
    [print(f"{i[0]} - {i[1]}") for i in alb_list]
    num = input("введите номер альбома, или пропустите(тогда будут фото из профиля)\n")
    alb = vk_client.albums[alb_list[int(num)][1]] if num else None
    count = input("введите количество, или пропустите(по умолчанию 5)\n")
    files_dict = get_vk_photos(vk_client, alb, int(count) if count else 5)
    print(f"{len(files_dict)} фото доступны")
    target = input("Ввеcти цифру - сохранить в гугл, букву - на яндекс\n")
    go_loader = GooClient(conf["path_gtoken"], conf["scopes"], conf["name"])
    ya_loader = Yandisc(conf["ya_token"], conf["name"])
    print(*[i["name"] for i in files_dict], sep="\n")
    if target.isdigit():
        go_load(go_loader, files_dict)
    elif target.isalpha():
        ya_load(ya_loader, files_dict)
    else:
        go_load(go_loader, files_dict)
        ya_load(ya_loader, files_dict)
