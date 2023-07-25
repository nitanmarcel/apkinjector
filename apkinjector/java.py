import glob
import os
import subprocess

import jdk
import time

from . import __JAVA_VERSION__, DEPENDENCIES, USER_DIRECTORIES
from .download import ProgressUnknown

from typing import Callable


def _download_java(progress_callback):
    pattern = os.path.join(USER_DIRECTORIES.user_data_dir,
                           f'jdk-{__JAVA_VERSION__}*', 'bin', 'java')
    paths = glob.glob(pattern)
    if paths:
        return paths[-1]
    if progress_callback:
        pregress = ProgressUnknown('java', None)
        progress_callback(pregress)
    path = jdk.install(str(__JAVA_VERSION__), jre=True,
                       path=USER_DIRECTORIES.user_data_dir)
    if path:
        return os.path.join(path, 'bin', 'java')
    return None

class Java:
    """
    A utility class for running Java commands.
    """

    @staticmethod
    def run_jar(jar_file : str, command : str) -> str:
        """Execute a jar file with the provided command.

        :param jar_file: Path to the jar file to be executed.
        :type jar_file: str
        :param command: Command to be passed when executing the jar file.
        :type command: str
        :return: Stdout of the command.
        :rtype: str
        """
        process = subprocess.run(
            f'{DEPENDENCIES.java} -jar {jar_file} {command}', shell=True, capture_output=True, text=True)
        return process.stdout
    
    @staticmethod
    def install(path: str = None, progress_callback: Callable = None) -> None:
        """Installs java

        :param path: Path to existing java if not found will use the system installed one or download it., defaults to None
        :type path: str, optional
        :param progress_callback:Callback to be called when install progress changes, defaults to None.
        :type progress_callback: Callable, optional
        
        """
        DEPENDENCIES.add_dependency(
            'java', path=path, fallback=_download_java, fallback_args=(progress_callback,))