import lzma
import os
import shutil
from typing import Callable, Union

import requests

from . import USER_DIRECTORIES
from .arch import ARCH
from .download import download_file
from .frida import Frida


class Gadget:
    """
    Frida Gadget utils.
    """
    @staticmethod
    def version() -> str:
        """
        Get recommended gadget version.

        :return: The recommended gadget version as string.
        :rtype: str
        """
        return Frida.version()

    @staticmethod
    def update(progress_callback: Callable = None) -> bool:
        """
        Downloads and updates the gadgets.

        :param progress_callback: Function to call when download progress changes, defaults to None.
        :type progress_callback: Callable, optional
        :return: True if the gadgets were successfully downloaded, False otherwise.
        :rtype: bool
        """
        version = Gadget.version()
        uri = 'https://api.github.com/repos/frida/frida/releases'
        response = requests.get(uri)
        response.raise_for_status()
        js = response.json()
        uri = None
        for release in js:
            if release['tag_name'] == version:
                uri = release['url']
        if not uri:
            return False
        response = requests.get(uri)
        response.raise_for_status()
        js = response.json()
        assets = js['assets']
        gadgets = []
        for asset in assets:
            if 'gadget' in asset['name'] and 'android' in asset['name']:
                gadgets.append(
                    [asset['name'], asset['browser_download_url']]
                )

        path = os.path.join(USER_DIRECTORIES.user_data_dir, 'gadgets', version)
        if os.path.isdir(path):
            shutil.rmtree(path)
        os.makedirs(path)
        for gadget in gadgets:
            target_path = os.path.join(path, gadget[0])
            output_path = download_file(
                gadget[1], target_path, progress_callback=progress_callback)
            with lzma.open(output_path) as _in, open(output_path.replace(".xz", ""), 'wb') as _out:
                _out.write(_in.read())
            os.remove(output_path)
        return True

    @staticmethod
    def get_gadget_path(arch: ARCH) -> Union[str, None]:
        """
        Gets the gadget path for the specified architecture.

        :param arch: The target architecture.
        :type arch: apkinjector.arch.ARCH
        :return: The path to the gadgets file if found, otherwise None.
        :rtype: Union[str, None]
        """
        version = Gadget.version()
        mappings = {
            ARCH.ARM: f'frida-gadget-{version}-android-arm.so',
            ARCH.ARM64: f'frida-gadget-{version}-android-arm64.so',
            ARCH.X64: f'frida-gadget-{version}-android-x86_64.so',
            ARCH.X86: f'frida-gadget-{version}-android-x86.so'
        }
        if arch not in mappings.keys():
            return None
        path = Gadget.get_gadget_dir()
        if not path:
            return path
        path = os.path.join(path, mappings[arch])
        if not os.path.exists(path):
            return None
        return path

    @staticmethod
    def get_gadget_dir() -> Union[str, None]:
        """
        Get the path where the gadgets are saved.

        :return: The path to the gadgets directory if found, otherwise None.
        :rtype: Union[str, None]
        """
        version = Frida.version()
        path = os.path.join(USER_DIRECTORIES.user_data_dir, 'gadgets', version)
        if os.path.isdir(path):
            return path
        return None
