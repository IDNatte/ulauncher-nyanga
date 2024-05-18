import os

import requests

from .constant import THUMB_META_URL, THUMB_PATH, TMP_PATH


def download_image(id, filename):
    response = requests.get(f"{THUMB_META_URL}/{id}/{filename}")
    if response.status_code == 200:
        with open(f"{THUMB_PATH}/{filename}", "wb") as f:
            f.write(response.content)
