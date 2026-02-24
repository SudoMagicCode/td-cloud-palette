import threading
import os
import time
import decoratedLog
#from requests import get
from queue import Queue

downloadLog = decoratedLog.DecoratedLog("- Threaded Downloader -")

MAX_WORKERS = 10


def _download(url: str, rootDir: str, queue: Queue) -> None:
    queue.put("Working")

    new_get_request = get(url, stream=True, timeout=10)
    name = url.split("/")[-1]
    fileName: str = f"{rootDir}/{name}"

    with open(fileName, "wb") as f:
        for chunk in new_get_request.iter_content(chunk_size=8192):
            f.write(chunk)

    queue.put("Ready")


def download(urlList: list[str], rootDir: str, targetOP) -> None:
    task_queue = Queue()
    workers = []
    targetOP.store("workers", workers)

    for each in range(MAX_WORKERS):
        worker_thread = threading.Thread(
            target=_download, args=(urlList[each], rootDir, task_queue))
        worker_thread.start()
        workers.append(worker_thread)
