import os
import subprocess
from typing import Callable

from . import __APKTOOL_VERSION__, DEPENDENCIES, USER_DIRECTORIES
from .download import download_file
from .java import Java


def _download_apktool(progress_callback=None):
    path = os.path.join(USER_DIRECTORIES.user_data_dir,
                        f'apktool_{__APKTOOL_VERSION__}.jar')
    if not os.path.isfile(path):
        uri = f'https://github.com/iBotPeaches/Apktool/releases/download/v{__APKTOOL_VERSION__}/apktool_{__APKTOOL_VERSION__}.jar'
        return download_file(uri, path, progress_callback)
    return path


class Apktool:
    """
    A wrapper class for the different Apktool commands.
    """

    @staticmethod
    def advanced():
        """
        Obtain advanced information of the Apktool.

        :return: The stdout from the command execution.
        :rtype: str
        """
        return Java.run_jar(DEPENDENCIES.apktool, '--advanced')

    @staticmethod
    def version():
        """
        Obtain the version of the Apktool.

        :return: The stdout from the command execution.
        :rtype: str
        """
        return Java.run_jar(DEPENDENCIES.apktool, '--version')

    @staticmethod
    def install_framework(framework_apk, framework_path=None, tag=None):
        """
        Install framework with provided options.

        :param framework_apk: The APK framework file to be installed.
        :type framework_apk: str
        :param framework_path: The directory where to store framework files, defaults to None.
        :type framework_path: str, optional
        :param tag: The tag for the framework file, defaults to None.
        :type tag: str, optional
        :return: The stdout from the command execution.
        :rtype: str
        """
        command = f'if {framework_apk}'
        if framework_path:
            command += f' --frame-path {framework_path}'
        if tag:
            command += f' --tag {tag}'
        return Java.run_jar(DEPENDENCIES.apktool, command)

    @staticmethod
    def decode(file_apk, force=False, output=None, framework_path=None, no_res=False, no_src=False, tag=None, force_manifest=False):
        """
        Decode an APK file with provided options.

        :param file_apk: The APK file to be decoded.
        :type file_apk: str
        :param force: Whether to force delete the destination directory, defaults to False.
        :type force: bool, optional
        :param output: The name of the output folder, defaults to None.
        :type output: str, optional
        :param framework_path: The directory containing framework files, defaults to None.
        :type framework_path: str, optional
        :param no_res: Whether to not decode resources, defaults to False.
        :type no_res: bool, optional
        :param no_src: Whether to not decode sources, defaults to False.
        :type no_src: bool, optional
        :param tag: A tag for the framework file, defaults to None.
        :type tag: str, optional
        :param force_manifest: Forces decode of AndroidManifest.xml regardless of decoding of resources parameter.
        :type force_manifest: str, optional
        :return: The stdout from the command execution.
        :rtype: str
        """
        command = f'd {file_apk}'
        if force:
            command += ' --force'
        if output:
            command += f' --output {output}'
        if framework_path:
            command += f' --frame-path {framework_path}'
        if no_res:
            command += ' --no-res'
        if no_src:
            command += ' --no-src'
        if tag:
            command += f' --frame-tag {tag}'
        if force_manifest:
            command += f' --force-manifest'
        return Java.run_jar(DEPENDENCIES.apktool, command)

    @staticmethod
    def build(app_path, force_all=False, output=None, framework_path=None, use_aapt2=False):
        """
        Build the unpacked apk from the given path with the provided options.

        :param app_path: The path of the app to build.
        :type app_path: str
        :param force_all: Whether to skip changes detection and build all files, defaults to False.
        :type force_all: bool, optional
        :param output: The name of the output APK file, defaults to None.
        :type output: str, optional
        :param framework_path: The directory containing framework files, defaults to None.
        :type framework_path: str, optional
        :param use_aapt2: Whether to use aapt 2 or no, defaults to False.
        :type use_aapt2: bool, optional.
        :return: The stdout from the command execution.
        :rtype: str
        """
        command = f'b {app_path}'
        if force_all:
            command += ' --force-all'
        if output:
            command += f' --output {output}'
        if framework_path:
            command += f' --frame-path {framework_path}'
        if use_aapt2:
            command += ' --use-aapt2'
        return Java.run_jar(DEPENDENCIES.apktool, command)

    @staticmethod
    def _run(command):
        if not DEPENDENCIES.apktool:
            return
        if DEPENDENCIES.apktool.endswith('.jar'):
            return Java.run_jar(DEPENDENCIES.apktool)
        process = subprocess.run(
            f'{DEPENDENCIES.apktool} {command}', shell=True, capture_output=True, text=True)
        return process.stdout

    @staticmethod
    def install(path: str = None, progress_callback: Callable = None) -> None:
        """
        Install apktool.

        :param path: Path to existing apktool.jar. If not found, will use the system installed one or download it. Defaults to None.
        :type path: str, optional
        :param progress_callback: Callback to be called when install progress changes, defaults to None.
        :type progress_callback: callable, optional
        """
        DEPENDENCIES.add_dependency(
            'apktool', path=path, fallback=_download_apktool, fallback_args=(progress_callback,))
