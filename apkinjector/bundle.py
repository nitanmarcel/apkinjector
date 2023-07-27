
from typing import List
import json
import os
import zipfile


class Bundle:
    """
    Tools to work with apk bundles (xapk and apks)
    """
    @staticmethod
    def extract(source: str, output_path: str) -> List[str]:
        """
        Extract a bundle (xapk and apks) to a given path.

        :param source: Path to the bundle.
        :type source: str
        :param output_path: Destination of the bundled.
        :type output_path: str
        :return: [bundle path, base apk]
        :rtype: List[str]
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
        if os.path.isfile(sai_manifestv1) or os.path.isfile(sai_manifestv2) or os.path.isfile(apkm_installer_url):
            base_apk = os.path.join(output_path, 'base.apk')
        else:
            manifest = os.path.join(output_path, 'manifest.json')
            with open(manifest, 'r') as m_file:
                manifest = json.load(m_file)
                for apk in manifest['split_apks']:
                    if apk['id'] == 'base':
                        base_apk = os.path.join(output_path, apk['file'])
        return [output_path, base_apk]

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
