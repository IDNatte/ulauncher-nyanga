import json
import re

from ulauncher.api.shared.action.ExtensionCustomAction import ExtensionCustomAction
from ulauncher.api.shared.item.ExtensionResultItem import ExtensionResultItem


def composer(data, init_data, extension):
    data_match = re.search(r"\[\s*{.*}\s*\]", data, re.DOTALL)
    if data_match:
        data_json_res = json.loads(data_match.group(0))
        for x in data_json_res:
            # cover_art_items = [
            #     (x.get("id"), y.get("attributes").get("fileName"))
            #     for y in x.get("relationships")
            #     if y.get("type") == "cover_art"
            # ]

            init_data.append(
                ExtensionResultItem(
                    icon="images/icon.png",
                    name=x.get("attributes").get("title").get("en") or "No title",
                    description="Read {0}".format(
                        x.get("attributes").get("title").get("en")
                    ),
                    on_enter=ExtensionCustomAction(
                        {
                            "open_app": False,
                            "nyr_bin": "{0}".format(
                                extension.preferences["nyanga_bin_path"]
                            ),
                            "mangaid": x.get("id"),
                            "manga_name": x.get("attributes").get("title").get("en"),
                            "open_bookmarked": None,
                        },
                        keep_app_open=True,
                    ),
                )
            )
