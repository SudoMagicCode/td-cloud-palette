import threading
import os
import time
import decoratedLog
from requests import get
from queue import Queue
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass

downloadLog = decoratedLog.DecoratedLog("- Threaded Downloader -")

MAX_WORKERS = 10


@dataclass
class dl_target:
    url: str
    path: str
    name: str
    author: str


def _download(info: dl_target) -> None:

    new_get_request = get(info.url, stream=True, timeout=10)

    if os.path.exists(info.path):
        pass
    else:
        with open(info.path, "wb") as f:
            for chunk in new_get_request.iter_content(chunk_size=8192):
                f.write(chunk)


def download(worker_info: list[dl_target], targetOP: OP) -> None:

    with ThreadPoolExecutor(max_workers=5) as worker:
        results = list(worker.map(_download, worker_info))
