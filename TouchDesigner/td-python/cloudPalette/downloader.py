from concurrent.futures import ThreadPoolExecutor, as_completed
import os
import time
import decoratedLog
from requests import get

downloadLog = decoratedLog.DecoratedLog("- Threaded Downloader -")

MAX_WORKERS = 10


def _download(url: str, rootDir: str) -> dict:
    start_time = time.time()

    new_get_request = get(url, stream=True, timeout=10)
    name = url.split("/")[-1]
    fileName: str = f"{rootDir}/{name}"

    end_time = time.time()
    elapsed_time = end_time - start_time

    with open(fileName, "wb") as f:
        for chunk in new_get_request.iter_content(chunk_size=8192):
            f.write(chunk)

    return {
        "url": url,
        "filename": fileName,
        "status": "success",
        "size_bytes": os.path.getsize(fileName),
        "time_taken_s": elapsed_time
    }


def download(urlList: list[str], rootDir: str) -> None:
    import threading

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        # Submit tasks to the executor and store Future objects
        # A Future object represents the eventual result of an asynchronous operation.
        future_to_url = {executor.submit(
            _download, url, rootDir): url for url in urlList}

        downloadLog.log_to_textport(
            f"Submitted {len(urlList)} download tasks.")
        downloadLog.log_to_textport("-" * 30)

        results = []
        # as_completed yields futures as they complete (in the order they finish)
        for future in as_completed(future_to_url):
            url = future_to_url[future]
            try:
                result = future.result()  # Get the result of the completed task
                results.append(result)
            except Exception as exc:
                downloadLog.log_to_textport(
                    f"[{threading.current_thread().name}] {url} generated an exception: {exc}")
                results.append({
                    "url": url,
                    "filename": None,
                    "status": "failed",
                    "error": f"Task execution failed: {str(exc)}",
                    "time_taken_s": None
                })

        for eachResult in results:
            if eachResult.get("status") == "success":
                downloadLog.log_to_textport(
                    f"  Size: {eachResult['size_bytes']} bytes, Time: {eachResult['time_taken_s']:.2f}s", includeDecorator=False)
