# import logging
# import subprocess

# from ulauncher.api.client.EventListener import EventListener
# from ulauncher.api.client.Extension import Extension
# from ulauncher.api.shared.action.ExtensionCustomAction import ExtensionCustomAction
# from ulauncher.api.shared.action.HideWindowAction import HideWindowAction
# from ulauncher.api.shared.action.RenderResultListAction import RenderResultListAction
# from ulauncher.api.shared.event import ItemEnterEvent, KeywordQueryEvent
# from ulauncher.api.shared.item.ExtensionResultItem import ExtensionResultItem

# from src.constant import THUMB_PATH
# from src.result_composer import composer
# from src.tempfile_man import create_temp, remove_temp
# from src.thumb_dl import download_image

# logger = logging.getLogger(__name__)


# class DemoExtension(Extension):
#     def __init__(self):
#         super().__init__()
#         self.subscribe(KeywordQueryEvent, KeywordQueryEventListener())
#         self.subscribe(ItemEnterEvent, ItemEnterEventListener())


# class ItemEnterEventListener(EventListener):
#     def on_event(self, event, extension):
#         logger.info(f"\n\n{event.get_data()}\n\n")
#         data = event.get_data()

#         if data.get("open_app"):
#             subprocess.run([data.get("nyr_bin")])

#         else:
#             subprocess.run(
#                 [
#                     data.get("nyr_bin"),
#                     "--extension",
#                     "--context",
#                     "open_manga",
#                     "--manga-id",
#                     data.get("mangaid"),
#                 ],
#             )

#         # remove_temp()

#         return RenderResultListAction(
#             [
#                 ExtensionResultItem(
#                     icon="images/icon.png",
#                     name=data.get("manga_name"),
#                     on_enter=HideWindowAction(),
#                 )
#             ]
#         )


# class KeywordQueryEventListener(EventListener):
#     def on_event(self, event, extension):
#         # create_temp()
#         data = [
#             ExtensionResultItem(
#                 icon="images/icon.png",
#                 name="Open Nyanga Read",
#                 description="Open Nyanga-Read Application",
#                 on_enter=ExtensionCustomAction(
#                     {
#                         "open_app": True,
#                         "nyr_bin": "{0}".format(
#                             extension.preferences["nyanga_bin_path"]
#                         ),
#                         "mangaid": None,
#                         "manga_name": None,
#                     },
#                     keep_app_open=True,
#                 ),
#             )
#         ]

#         if event.get_argument():
#             result = subprocess.run(
#                 [
#                     extension.preferences.get("nyanga_bin_path"),
#                     "--extension",
#                     "--context",
#                     "search_manga",
#                     "--manga-name",
#                     event.get_argument(),
#                 ],
#                 capture_output=True,
#                 text=True,
#             )

#             composer(result, data, extension)

#         return RenderResultListAction(data)


# if __name__ == "__main__":
#     DemoExtension().run()

import logging
import queue
import subprocess
import threading

from ulauncher.api.client.EventListener import EventListener
from ulauncher.api.client.Extension import Extension
from ulauncher.api.shared.action.ExtensionCustomAction import ExtensionCustomAction
from ulauncher.api.shared.action.HideWindowAction import HideWindowAction
from ulauncher.api.shared.action.RenderResultListAction import RenderResultListAction
from ulauncher.api.shared.event import ItemEnterEvent, KeywordQueryEvent
from ulauncher.api.shared.item.ExtensionResultItem import ExtensionResultItem

from src.constant import THUMB_PATH
from src.result_composer import composer
from src.tempfile_man import create_temp, remove_temp
from src.thumb_dl import download_image

logger = logging.getLogger(__name__)


class DemoExtension(Extension):
    def __init__(self):
        super().__init__()
        self.subscribe(KeywordQueryEvent, KeywordQueryEventListener())
        self.subscribe(ItemEnterEvent, ItemEnterEventListener())


class ItemEnterEventListener(EventListener):
    def on_event(self, event, extension):
        logger.info(f"\n\n{event.get_data()}\n\n")
        data = event.get_data()

        command = [data.get("nyr_bin")]

        if not data.get("open_app"):
            command.extend(
                [
                    "--extension",
                    "--context",
                    "open_manga",
                    "--manga-id",
                    data.get("mangaid"),
                ]
            )

        process = subprocess.Popen(command)
        process.wait()

        return RenderResultListAction(
            [
                ExtensionResultItem(
                    icon="images/icon.png",
                    name=data.get("manga_name"),
                    on_enter=HideWindowAction(),
                )
            ]
        )


class KeywordQueryEventListener(EventListener):
    def on_event(self, event, extension):
        # create_temp()
        data = [
            ExtensionResultItem(
                icon="images/icon.png",
                name="Open Nyanga Read",
                description="Open Nyanga-Read Application",
                on_enter=ExtensionCustomAction(
                    {
                        "open_app": True,
                        "nyr_bin": extension.preferences["nyanga_bin_path"],
                        "mangaid": None,
                        "manga_name": None,
                    },
                    keep_app_open=True,
                ),
            )
        ]

        if event.get_argument():
            command = [
                extension.preferences.get("nyanga_bin_path"),
                "--extension",
                "--context",
                "search_manga",
                "--manga-name",
                event.get_argument(),
            ]

            def enqueue_output(pipe, queue):
                for line in iter(pipe.readline, ""):
                    queue.put(line)
                pipe.close()

            process = subprocess.Popen(
                command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
            )

            stdout_queue = queue.Queue()
            stderr_queue = queue.Queue()

            stdout_thread = threading.Thread(
                target=enqueue_output, args=(process.stdout, stdout_queue)
            )
            stderr_thread = threading.Thread(
                target=enqueue_output, args=(process.stderr, stderr_queue)
            )

            stdout_thread.start()
            stderr_thread.start()

            # Wait for the process to complete
            process.wait()

            # Ensure threads have finished
            stdout_thread.join()
            stderr_thread.join()

            # Collect all output
            stdout_lines = []
            stderr_lines = []

            while not stdout_queue.empty():
                stdout_lines.append(stdout_queue.get())

            while not stderr_queue.empty():
                stderr_lines.append(stderr_queue.get())

            stdout_output = "".join(stdout_lines)
            stderr_output = "".join(stderr_lines)

            if stderr_output:
                logger.error(stderr_output)

            # logger.info("\n\n{0}\n\n".format(stdout_output))
            composer(stdout_output, data, extension)

        return RenderResultListAction(data)


if __name__ == "__main__":
    DemoExtension().run()
