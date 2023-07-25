import subprocess
from typing import NoReturn, Union

from . import DEPENDENCIES, utils
from .arch import ARCH


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
                f'adb {command}', shell=True, capture_output=True, text=True, timeout=5)
            return process.stdout.strip()
        except subprocess.TimeoutExpired:
            return None


DEPENDENCIES.add_dependency('adb', required=None)
