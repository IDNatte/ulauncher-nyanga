import concurrent.futures as fu
import json
import re

from ulauncher.api.shared.action.ExtensionCustomAction import ExtensionCustomAction
from ulauncher.api.shared.item.ExtensionResultItem import ExtensionResultItem

from .constant import THUMB_PATH
from .thumb_dl import download_image


def composer(data, init_data, extension):
    data_match = re.search(r"\[.*\]", data.stdout, re.DOTALL)
    if data_match:
        data_json_res = json.loads(data_match.group(0))
        for x in data_json_res:
            cover_art_items = [
                (x.get("id"), y.get("attributes").get("fileName"))
                for y in x.get("relationships")
                if y.get("type") == "cover_art"
            ]

            with fu.ThreadPoolExecutor() as downloader:
                fu_data = [
                    downloader.submit(download_image, id, file_name)
                    for id, file_name in cover_art_items
                ]
                fu.wait(fu_data)

            init_data.append(
                ExtensionResultItem(
                    icon="{0}/{1}".format(
                        THUMB_PATH,
                        next(
                            (
                                rel.get("attributes").get("fileName")
                                for rel in x.get("relationships")
                                if rel.get("type") == "cover_art"
                            ),
                            "../images/icon.png",
                        ),
                    ),
                    name=x.get("attributes").get("title").get("en"),
                    description="Read {0}".format(
                        x.get("attributes").get("title").get("en")
                    ),
                    on_enter=ExtensionCustomAction(
                        {
                            "open_app": False,
                            "nyr_bin": f"{extension.preferences['nyanga_bin_path']}",
                            "mangaid": x.get("id"),
                            "manga_name": x.get("attributes").get("title").get("en"),
                        },
                        keep_app_open=True,
                    ),
                )
            )
