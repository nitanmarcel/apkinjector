
from typing import List, Union
import json
import re
import os
import zipfile

from dataclasses import dataclass
from .arch import ARCH
from .utils import arch_to_abi

@dataclass
class ConfigArch:
    """
    A Data class representing the architecture information in a split APK file.
    
    :param str file_name: The name of the APK file.
    :param str arch: The architecture type of the APK file ('ARM', 'ARM64', 'X86', 'X64').
    """

    file_name: str
    arch: str

@dataclass
class ConfigLocale:
    """
    A Data class representing the locale information in a split APK file.

    :param str file_name: A string representing the name of the APK file.
    :param str locale: A string indicating the locale config of the APK file.
    """

    file_name: str
    locale: str

@dataclass
class ConfigDpi:
    """
    A Data class representing the DPI information in a split APK file.

    :param str file_name: The name of the APK file.
    :param str dpi: A string representing the screen DPI config of the APK.
    """

    file_name: str
    dpi: str

@dataclass
class BundleInfo:
    """
    A data class representing general information about an Android Bundle file.

    :param str base_apk: The name of the base APK file extracted from the Android Bundle.
    :param List[Union[ConfigDpi, ConfigLocale, ConfigArch]] configs: Configurations of the APK files extracted from the Android Bundle.
    """

    base_apk: str
    configs: List[Union[ConfigDpi, ConfigLocale, ConfigArch]]

class Bundle:
    """
    Tools to work with apk bundles (xapk and apks)
    """
    @staticmethod
    def extract(source: str, output_path: str) -> BundleInfo:
        """
        Extract a bundle (xapk and apks) to a given path.

        :param source: Path to the bundle.
        :type source: str
        :param output_path: Destination of the bundled.
        :type output_path: str
        :return: BundleInfo class containing the name of the base apk and configuration ifno.
        :rtype: BundleInfo
        """
        name = os.path.basename(source)[:-5]
        base_apk = None
        if os.path.exists(output_path):
            output_path = os.path.join(output_path, name)
        os.makedirs(output_path)
        with zipfile.ZipFile(source) as zip:
            zip.extractall(output_path)
        sai_manifestv1 = os.path.join(output_path, 'meta.sai_v1.json')
        sai_manifestv2 = os.path.join(output_path, 'meta.sai_v2.json')
        apkm_installer_url = os.path.join(output_path, 'APKM_installer.url')
        base_apk = None
        configs = []
        matches = [None]

        if os.path.isfile(sai_manifestv1) or os.path.isfile(sai_manifestv2) or os.path.isfile(apkm_installer_url):       
            base_apk = 'base.apk'
        else:
            manifest = os.path.join(output_path, 'manifest.json')
            with open(manifest, 'r') as m_file:
                manifest = json.load(m_file)
                for apk in manifest['split_apks']:
                    if apk['id'] == 'base':
                        base_apk = apk['file']
        files = os.listdir(output_path)
        for file in files:
            if file.endswith('.apk'):
                if f'.{arch_to_abi(ARCH.ARM64)}.' in file and file not in matches:
                    configs.append(ConfigArch(file, ARCH.ARM64))
                    matches.append(file)
                if f'.{arch_to_abi(ARCH.ARM)}.' in file and file not in matches:
                    configs.append(ConfigArch(file, ARCH.ARM))
                    matches.append(file)

                if f'.{arch_to_abi(ARCH.ARM64).replace("-", "_")}.' in file and file not in matches:
                    configs.append(ConfigArch(file, ARCH.ARM64))
                    matches.append(file)
                if f'.{arch_to_abi(ARCH.ARM).replace("-", "_")}.' in file and file not in matches:
                    configs.append(ConfigArch(file, ARCH.ARM))
                    matches.append(file)

                if f'.{arch_to_abi(ARCH.X64)}.' in file and file not in matches:
                    configs.append(ConfigArch(file, ARCH.X64))
                    matches.append(file)
                if f'.{arch_to_abi(ARCH.X86)}.' in file and file not in matches:
                    configs.append(ConfigArch(file, ARCH.X86))
                    matches.append(file)
                        
                # Check for locale
                locale_match = re.search(r'config\.([a-z]{2}(?:_r[A-Z]{2})?)\.apk', file)
                if locale_match and file not in matches:
                    configs.append(ConfigLocale(file, locale_match.group(1)))
                
                # Check for dpi
                dpi_match = re.search(r'config\.(.*?)\.apk', file)
                if dpi_match and dpi_match.group(1).endswith('dpi') and file not in matches:
                    configs.append(ConfigDpi(file, dpi_match.group(1).replace('dpi', '')))
                    matches.append(file)
        info = BundleInfo(base_apk, configs)
        return info

    @staticmethod
    def repack(source: str, output_path: str) -> str:
        """
        Repacks a bundle (xapk and apks) to a given path.

        :param source: Path to the extracted bundle.
        :type source: str
        :param output_path: Path to where to save the bundle file.
        :type output_path: str
        :return: Location of the repacked bundle.
        """
        with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zip:
            for foldername, subfolders, filenames in os.walk(source):
                for filename in filenames:
                    abspath = os.path.join(foldername, filename)
                    relpath = os.path.relpath(abspath, source)
                    zip.write(abspath, arcname=relpath)
        return output_path

    @staticmethod
    def is_bundle(source: str) -> bool:
        """
        Checks if the source is a bundle or not.

        :param source: Source to check.
        :type source: str
        :return: True if it's a bundle, False otherwise.
        :rtype: bool
        """
        name = os.path.basename(source)
        return name.endswith('.xapk') or name.endswith('.apks') or name.endswith('.apkm')
