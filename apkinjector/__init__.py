import logging
import os

from appdirs import AppDirs

from .dependencies import DependenciesManager
from .logger import ApkInjectorLogger

LOG = ApkInjectorLogger(__name__)

USER_DIRECTORIES: AppDirs = AppDirs(__name__, 'nitanmarcel')

if not os.path.isdir(USER_DIRECTORIES.user_data_dir):
    os.makedirs(USER_DIRECTORIES.user_data_dir)
if not os.path.isdir(USER_DIRECTORIES.user_cache_dir):
    os.makedirs(USER_DIRECTORIES.user_cache_dir)


DEPENDENCIES = DependenciesManager(USER_DIRECTORIES.user_data_dir)

__APKTOOL_VERSION__ = '2.8.0'
__UBER_SIGNER_VERSION__ = '1.3.0'
__JAVA_VERSION__ = '17'

__PLUGIN_DATA__ = 'https://raw.githubusercontent.com/nitanmarcel/apkinjector/main/plugins/plugins.json'

if DEPENDENCIES.has_missing_required_dependency():
    LOG.error('Some dependencies are missing.')
