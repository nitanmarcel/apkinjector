import subprocess
from typing import Callable, Union

from . import DEPENDENCIES, USER_DIRECTORIES, utils
from .arch import ARCH
from .download import download_file

import os
import platform
import zipfile

def _download_adb(progress_callback=None):
    def _get_bin():
        if plat in ['Linux', 'Darwin']:
            exe = os.path.join(USER_DIRECTORIES.user_data_dir, 'platform-tools', 'adb')
            os.chmod(exe, 0o755) # set executable permission
            return exe
        if plat == 'Windows':
            return os.path.join(USER_DIRECTORIES.user_data_dir, 'platform-tools', 'adb')
        return None
    plat = platform.system()
    uri = None
    if plat == 'Linux':
        uri = 'https://dl.google.com/android/repository/platform-tools_r29.0.5-linux.zip'
    if plat == 'Windows':
        uri = 'https://dl.google.com/android/repository/platform-tools_r29.0.5-windows.zip'
    if plat == 'Darwin':
        uri = 'https://dl.google.com/android/repository/platform-tools_r29.0.5-darwin.zip'
    
    path = os.path.join(USER_DIRECTORIES.user_data_dir, 'platform-tools')
    if os.path.isdir(path):
        return _get_bin()
    downloaded = download_file(uri, f'{path}.zip', progress_callback)
    with zipfile.ZipFile(downloaded, 'r') as ref:
        ref.extractall(USER_DIRECTORIES.user_data_dir)
    return _get_bin()


class Adb:
    """
    A utility class for running adb commands.
    """
    @staticmethod
    def get_architecture() -> Union[ARCH, None]:
        """
        Get phone architecture as apkpatcher.arch.ARCH.

        This function serves as a shorthand for ``apkpatcher.utils.abi_to_arch(apkpatcher.adb.Adb.get_prop('ro.product.cpu.abi'))``.

        :return: apkpatcher.arch.ARCH if adb is installed and a device is connected. Otherwise, it returns None.
        :rtype: Union[str, None]
        """
        res = Adb.get_prop('ro.product.cpu.abi')
        if not res:
            return None
        return utils.abi_to_arch(res)

    @staticmethod
    def get_prop(prop: str) -> Union[str, None]:
        """
        Calls ``adb shell getprop {prop}``.

        :param prop: Prop to retrieve
        :type prop: str
        :return: Returns prop from device if adb is installed and a device is connected. Otherwise, it returns None.
        :rtype: Union[str, None]
        """
        return Adb.shell(f'getprop {prop}')

    @staticmethod
    def wait_for_device() -> None:
        """
        Waits for a device to be connected. If adb is not installed, it will skip without waiting.
        """
        if not DEPENDENCIES.adb:
            return None
        return Adb.run(f'wait-for-device')

    @staticmethod
    def shell(command: str) -> str:
        """
        Run an adb shell command.

        :param command: Command to be ran.
        :type command: str
        :return: Output of the command if adb is installed and a device is connected. Otherwise, it returns None.
        :rtype: str
        """
        return Adb.run(f'shell {command}')

    @staticmethod
    def run(command: str) -> Union[str, None]:
        """
        Bare method to run adb commands.

        :param command: Command to be run.
        :type command: str
        :return: Output of the command if adb is installed and a device is connected. Otherwise, it returns None.
        :rtype: Union[str, None]
        """
        if not DEPENDENCIES.adb:
            return None
        try:
            process = subprocess.run(
                f'{DEPENDENCIES.adb} {command}', shell=True, capture_output=True, text=True, timeout=5)
            return process.stdout.strip()
        except subprocess.TimeoutExpired:
            return None
        
    @staticmethod
    def install(path: str = None, progress_callback: Callable = None) -> None:
        """
        Install adb tools.

        :param path: Path to existing adb executable. If not found, will use the system installed one or download it. Defaults to None.
        :type path: str, optional
        :param progress_callback: Callback to be called when install progress changes, defaults to None.
        :type progress_callback: callable, optional
        """
        DEPENDENCIES.add_dependency(
            'adb', path=path, fallback=_download_adb, fallback_args=(progress_callback,))
