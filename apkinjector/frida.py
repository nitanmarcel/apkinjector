import subprocess

import requests

from . import DEPENDENCIES


class Frida:
    """
    A utility class for running Frida commands.
    """

    @staticmethod
    def version():
        """
        Obtain the version of frida.

        :return: The stdout from the command execution.
        :rtype: str
        """
        if DEPENDENCIES.frida is not None:
            process = subprocess.run(
                f'{DEPENDENCIES.frida} --version', shell=True, capture_output=True, text=True)
            return process.stdout.strip()
        uri = f"https://api.github.com/repos/frida/frida/releases/latest"
        response = requests.get(uri)
        js = response.json()
        return js['tag_name']


DEPENDENCIES.add_dependency('frida', required=False)
