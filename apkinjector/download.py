from dataclasses import dataclass
from typing import Callable, Optional

import os
import shutil
import requests

from . import LOG, USER_DIRECTORIES


@dataclass
class ProgressDownloading:
    filename: str
    progress: int


@dataclass
class ProgressFailed:
    filename: str
    status_code: int


@dataclass
class ProgressCompleted:
    filename: str
    path: str

@dataclass
class ProgressUnknown:
    filename: str
    path: str


def download_file(url: str, target_path: str, progress_callback: Optional[Callable] = None) -> str:
    """
    Download a file from a given URL and save it on the target path.

    :param url: The URL from where file needs to be downloaded.
    :type url: str
    :param target_path: The path on local system where the downloaded file should be saved.
    :type target_path: str
    :param progress_callback: Function to call when the progress changes, defaults to None.
    :type progress_callback: Optional[Callable]
    :return: The target path where the file has been downloaded.
    :rtype: str
    """
    def _callable(args):
        if progress_callback is not None:
            progress_callback(args)
    file_name = target_path.split('/')[-1]
    tmp_path = os.path.join(USER_DIRECTORIES.user_cache_dir, "downloads")
    if not os.path.exists(tmp_path):
        os.mkdir(tmp_path)

    tmp_path = os.path.join(tmp_path, file_name)

    if os.path.isfile(tmp_path):
        os.remove(tmp_path)
    response = requests.get(url, stream=bool(progress_callback))
    total_length = response.headers.get('content-length')
    total_length = int(total_length)

    if response.status_code != 200:
        _callable(ProgressFailed(filename=file_name,
                  status_code=response.status_code))
        return
    _callable(ProgressDownloading(filename=file_name, progress=0))
    with open(tmp_path, 'wb') as f:
        if not bool(progress_callback):
            f.write(response.content)
        else:
            downloaded = 0
            for chunk in response.iter_content(chunk_size=1020):
                if chunk:
                    downloaded += len(chunk)
                    percentage = int(downloaded * 100 / total_length)
                    _callable(ProgressDownloading(file_name, percentage))
                    f.write(chunk)
    if os.path.isfile(tmp_path):
        shutil.move(tmp_path, target_path)
    _callable(ProgressCompleted(file_name, target_path))

    return target_path
