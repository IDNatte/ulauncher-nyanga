import os
import shutil

from .constant import THUMB_PATH, TMP_PATH


def create_temp():
    if not os.path.isdir(TMP_PATH):
        os.makedirs(THUMB_PATH)


def remove_temp():
    if os.path.isdir(TMP_PATH):
        shutil.rmtree(TMP_PATH)
