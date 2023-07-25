import os
from typing import Callable, List, Optional

from . import __UBER_SIGNER_VERSION__, DEPENDENCIES, USER_DIRECTORIES
from .download import download_file
from .java import Java


def _download_uberapksigner(progress_callback=None):
    path = os.path.join(USER_DIRECTORIES.user_data_dir,
                        f'uber-apk-signer-{__UBER_SIGNER_VERSION__}.jar')
    if not os.path.isfile(path):
        uri = f'https://github.com/patrickfav/uber-apk-signer/releases/download/v{__UBER_SIGNER_VERSION__}/uber-apk-signer-{__UBER_SIGNER_VERSION__}.jar'
        return download_file(uri, path, progress_callback)
    return path


class UberApkSigner:
    """
    Execute uber-apk-signer commands
    """
    @staticmethod
    def version():
        """
        Obtain the version of uber-apk-signer.

        :return: The stdout from the command execution.
        :rtype: str
        """
        return Java.run_jar(DEPENDENCIES.uber_apk_signer, '--version')

    @staticmethod
    def sign(apks: str, allow_resign: Optional[bool] = False, debug: Optional[bool] = False,
             dry_run: Optional[bool] = False, ks: Optional[str] = None, ks_alias: Optional[str] = None,
             ks_debug: Optional[str] = None, ks_key_pass: Optional[str] = None, ks_pass: Optional[str] = None,
             lineage: Optional[str] = None, out: Optional[str] = None, overwrite: Optional[bool] = False,
             skip_zip_align: Optional[bool] = False, only_verify: Optional[bool] = False,
             zip_align_path: Optional[str] = None, verify_sha256: Optional[str] = None) -> str:
        """
        Sign an APK or a set of APKs.

        :return: The stdout from the command execution.
        :rtype: str
        """

        command = f'-a {apks}'

        if allow_resign:
            command += " --allowResign"

        if debug:
            command += " --debug"

        if dry_run:
            command += " --dryRun"

        if ks:
            command += f' --ks {ks}'

        if ks_alias:
            command += f' --ksAlias {ks_alias}'

        if ks_debug:
            command += f' --ksDebug {ks_debug}'

        if ks_key_pass:
            command += f' --ksKeyPass {ks_key_pass}'

        if ks_pass:
            command += f' --ksPass {ks_pass}'

        if lineage:
            command += f' -l {lineage}'

        if out:
            command += f' -o {out}'

        if overwrite:
            command += " --overwrite"

        if skip_zip_align:
            command += " --skipZipAlign"

        if only_verify:
            command += " -y"

        if zip_align_path:
            command += f' --zipAlignPath {zip_align_path}'

        if verify_sha256:
            command += f' --verifySha256 {verify_sha256}'

        return Java.run_jar(DEPENDENCIES.uber_apk_signer, command)

    @staticmethod
    def install(path: str = None, progress_callback: Callable = None) -> None:
        """
        Install uber-apk-signer.

        :param path: Path to existing uber-apk-signer.jar. If not found, will use the system installed one or download it. Defaults to None.
        :type path: str, optional
        :param progress_callback: Callback to be called when install progress changes, defaults to None.
        :type progress_callback: callable, optional
        """
        DEPENDENCIES.add_dependency(
            'uber-apk-signer', path=path, fallback=_download_uberapksigner, fallback_args=(progress_callback,))
