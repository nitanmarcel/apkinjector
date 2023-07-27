import os
import sys
import time
import zipfile

import click
import json
import shutil
import requests
import tempfile
from colorama import Fore

from . import LOG, USER_DIRECTORIES, __PLUGIN_DATA__
from .adb import Adb
from .apktool import Apktool
from .java import Java
from .arch import ARCH
from .download import ProgressCompleted, ProgressDownloading, ProgressFailed, ProgressUnknown
from .frida import Frida
from .gadget import Gadget
from .injector import Injector
from .plugins import _PluginLoader, main
from .uber_apk_signer import UberApkSigner
from .bundle import Bundle, ConfigArch, ConfigDpi, ConfigLocale
from .download import download_file
from .manifest import Manifest

def _clear_cache(func):
    def inner(*args, **kwargs):
        func(*args, **kwargs)
        shutil.rmtree(USER_DIRECTORIES.user_cache_dir)
        os.makedirs(USER_DIRECTORIES.user_cache_dir)
    return inner


def _install_callback(progress):
    if isinstance(progress, ProgressDownloading):
        sys.stdout.write(
            Fore.GREEN + f'\r[+] Downloading {progress.filename} - {progress.progress:03d}%')
        sys.stdout.flush()
    if isinstance(progress, ProgressFailed):
        sys.stdout.write(
            Fore.RED + f'[*] Download failed with status: {progress.status_code}')
    if isinstance(progress, ProgressCompleted):
        sys.stdout.write('\n')
    if isinstance(progress, ProgressUnknown):
        LOG.info('Downloading {} this might take a while...', progress.filename)


@_clear_cache
def _inject(apk, libraries, include, activity, output, override, use_aapt):
    if not os.path.isfile(apk):
        LOG.error('{} - not such file.', apk)
    for lib in libraries:
        if not os.path.isfile(lib):
            LOG.error('{} - not such file.', lib)
    
    if include:
        for i in include:
            if not os.path.isfile(i):
                LOG.error('Include {} is not a valid file.', include)

    apk_name, ext =  os.path.splitext(apk)
    workdir = os.path.join(USER_DIRECTORIES.user_cache_dir, apk_name)
    entry_lib = libraries[0]

    _, _ext = os.path.splitext(output)
    if not _ext:
        # is file
        tmp_output = output
        if os.path.isdir(output):
            tmp_output = os.path.join(output, f'{apk_name}_patched{ext}' if not override else apk)
        else:
            if tmp_output.endswith(os.sep):
                tmp_output = tmp_output.rsplit(os.sep, 1)[0]
        if os.path.exists(tmp_output):
            timestamp = int(time.time())
            tmp_output = os.path.join(output, f'{apk_name}_patched_{timestamp}{ext}')
        output = tmp_output
    else:
        if os.path.exists(output) and not override:
            LOG.error('{} already exists.', output)

    is_bundle = Bundle.is_bundle(apk)

    output_bundle = None
    bundle_info = None

    if is_bundle:
        LOG.info('Extracting split apks...')
        output_bundle = f'{workdir}_bundle'
        if os.path.exists(output_bundle):
            shutil.rmtree(output_bundle)
        bundle_info = Bundle.extract(apk, output_bundle)

    targets = []

    if bundle_info and bundle_info.configs:
        for config in bundle_info.configs:
            if isinstance(config, ConfigArch):
                for lib in libraries.copy():
                    lib_arch = Injector.guess_arch_from_lib(lib)
                    if lib_arch == config.arch:
                        target_split = os.path.join(output_bundle, config.file_name)
                        targets.append([target_split, lib])
                        libraries.remove(lib)
    for lib in libraries:
        if is_bundle:
            target_split = os.path.join(output_bundle, bundle_info.base_apk)
            targets.append([target_split, lib])
        else:
            targets.append([output, lib])

    Apktool.install(progress_callback=_install_callback)
    LOG.info('Using apktool: {}', Apktool.version())

    base = os.path.join(output_bundle, bundle_info.base_apk) if is_bundle else apk
    # extract base
    LOG.info('Extracting {}', base)
    Apktool.decode(base, force=True, output=workdir, framework_path=f'{workdir}_framework')

    manifest_path = os.path.join(workdir, 'AndroidManifest.xml')
    target_activity = None
    if activity:
        for activities in Manifest.get_activities(manifest_path):
            for i in activities:
                if activity in i:
                    target_activity = i
                    break
    else:
        target_activity = Manifest.get_main_activity(manifest_path)
    if not target_activity:
        LOG.error('{} did not match any activities', activity)
    
    LOG.info('Found target activity {}', target_activity)

    entrypoint = None
    for file in os.listdir(workdir):
        if file.startswith('smali'):
            entrypoint_tmp = os.path.join(
            workdir, file, target_activity.replace('.', '/') + '.smali')
            if os.path.isfile(entrypoint_tmp):
                entrypoint = entrypoint_tmp
                break  
    if not entrypoint:
        LOG.error('Failed to find smali file for activity {}', target_activity)
        
    LOG.info('Injecting smali loader into {}.', target_activity)
    injected = Injector.inject_library(entry_lib, workdir, entrypoint, include, skip_copy=True) # Copying will be done for each target bellow
    if not injected:
        LOG.error('Something wen\'t wrong when injecting into target..')
    LOG.info('Repacking {} -> {}', base if is_bundle else apk, base if is_bundle else output)
    Apktool.build(workdir, output=base if is_bundle else output, framework_path=f'{workdir}_framework', use_aapt2=use_aapt)

    for target in targets:
        apk_target = target[0]
        lib_target = target[1]
        if os.path.exists(workdir):
            shutil.rmtree(workdir)
        os.makedirs(workdir)
        LOG.info('Extracting {}', apk_target)
        with zipfile.ZipFile(apk_target, 'r') as ref:
            ref.extractall(workdir)
        LOG.info('Injecting {} in {}', lib_target, apk_target)
        injected = Injector.inject_library(lib_target, workdir, smali_path=None, extra_files=include)
        if not injected:
            LOG.error('Something wen\'t wrong when injecting into target..')
        LOG.info('Repacking {} -> {}', apk_target, apk_target if is_bundle else output)
        with zipfile.ZipFile(apk_target if is_bundle else output, 'w') as ref:
            for root, dirs, files in os.walk(workdir):
                for file in files:
                    ref.write(os.path.join(root, file), 
                        os.path.relpath(os.path.join(root, file), 
                                        workdir))
    
    apks = []
    if is_bundle:
        apks = [os.path.join(output_bundle, apk) for apk in os.listdir(output_bundle) if apk.endswith('.apk')]
    else:
        apks = [output,]
    
    LOG.info('Signing {}', ' '.join([os.path.basename(apk) for apk in apks]))
    UberApkSigner.install(progress_callback=_install_callback)

    LOG.info('Using uber-apk-signer {}', UberApkSigner.version().split()[-1])

    UberApkSigner.sign(apks, allow_resign=True, overwrite=True)

    if is_bundle:
        LOG.info('Repacking bundle')
        cache_bundle = os.path.join(USER_DIRECTORIES.user_cache_dir, f'cached.{ext}')
        Bundle.repack(f'{workdir}_bundle', cache_bundle)
        if os.path.isfile(output):
            os.remove(output)
        shutil.copyfile(cache_bundle, output)
    LOG.info('DONE! {}', output)

    ### Clear cache
  
@main.command(help='Inject a shared library (*.so) in a target apk.')
@click.argument('apk')
@click.option('--library', required=True, multiple=True, help='Shared library (*.so) to inject. If multiple are given, only the first one will be automatically loaded.')
@click.option('--include', multiple=True, required=False, help='Extra files to include in the lib folder. Can be used multiple times to include more files.')
@click.option('--activity', required=False, help='Name of the activity to inject into. If unspecified, the main activity will be injected.')
@click.option('--output', required=False, default=os.getcwd(), help='Custom path where the patched apk should be saved.')
@click.option('--override', is_flag=True, help='Override apk in place.')
@click.option('--aapt2', required=False, help='Either to use aapt2 when building the apk or not.')
def inject(apk, library, include, activity, output, override, aapt2):
    Java.install(progress_callback=_install_callback)
    _inject(apk, library, include, activity, output, override, aapt2)


@main.command(help='Inject a frida gadget in a target apk.')
@click.argument('apk')
@click.option('--script', required=False, help='Inject a javascript to be loaded when the gadget starts.')
@click.option('--codeshare', required=False, help='Same as --script but uses Frida Codeshare as the source javascript.')
@click.option('--arch', required=False, help='Architecture to inject for. If empty --all, --adb or --gadget must be specified.')
@click.option('--adb', is_flag=True, help='Use adb (if installed) to detect device architecture.')
@click.option('--activity', required=False, help='Name of the activity to inject into. If unspecified, the main activity will be injected.')
@click.option('--output', required=False, default=os.getcwd(), help='Custom path where the patched apk should be saved.')
@click.option('--override', is_flag=True, help='Override apk in place.')
@click.option('--aapt2', required=False, help='Either to use aapt2 when building the apk or not.')
def frida(apk, script, codeshare, arch, adb, activity, output, override, aapt2):
    if arch:
        if arch not in [ARCH.ARM, ARCH.ARM64, ARCH.X86, ARCH.X64]:
            LOG.error('{} not a supported arch: {}, {}, {}, {}',
                      arch, ARCH.ARM, ARCH.ARM64, ARCH.X86, ARCH.X64)
        Java.install(progress_callback=_install_callback)
        gadget = Gadget.get_gadget_path(arch)
        if not gadget:
            Gadget.update(_install_callback)
            gadget = Gadget.get_gadget_path(arch)
    elif adb:
        arch = Adb.get_architecture()
        if not arch:
            LOG.info('Waiting for adb device...')
            Adb.wait_for_device()
            arch = Adb.get_architecture()
        if not arch:
            LOG.error(
                'Failed to connect to any device. Make sure you have adb installed, and the device is properly connected.')
        gadget = Gadget.get_gadget_path(arch)
        if not gadget:
            Gadget.update(_install_callback)
            gadget = Gadget.get_gadget_path(arch)
    else:
        LOG.error('--arch or --adb is missing.')
    if os.path.exists(gadget):
        gadget_tmp = os.path.join(
            USER_DIRECTORIES.user_cache_dir, 'libfrida-gadget.so')
        shutil.copy(gadget, gadget_tmp)
    if script:
        if not os.path.isfile(script):
            LOG.error('Not a valid script file: {}', script)
        script_tmp = os.path.join(
            USER_DIRECTORIES.user_cache_dir, 'libhook.js.so')
        shutil.copyfile(script, script_tmp)
        script = [script_tmp,]
    if codeshare:
        if codeshare.endswith('/'):
            codeshare = uri = uri[:-1]
            project_url = f"https://codeshare.frida.re/api/project/{uri}/"
            script = os.path.join(
                USER_DIRECTORIES.user_cache_dir, 'libhook.js.so')
            download_file(project_url, script, _install_callback)
    if script or codeshare:
        config = {
            "interaction":
            {
                "type": "script",
                "address": "127.0.0.1",
                "port": 27042,
                "path": "./libhook.js.so",
                "on_port_conflict": "pick-next",
                "on_load": "resume"
            }
        }
        config_path = os.path.join(
            USER_DIRECTORIES.user_cache_dir, 'libfrida-gadget.config.so')
        with open(config_path, 'w') as f:
            f.write(json.dumps(config))
        script.append(config_path)
    _inject(apk, [gadget_tmp,], script, activity, output, override, aapt2)


@main.command(help='Apk utils')
@click.argument('apk')
@click.option('--activities', is_flag=True, help='Gets all activities')
@click.option('--permissions', is_flag=True, help='Gets all permissions')
@click.option('--libraries', is_flag=True, help='Gets all libraries')
@click.option('--recievers', is_flag=True, help='Gets all receivers')
def apk(apk, activities, permissions, libraries, recievers):
    def _parse_apk():
        Java.install(progress_callback=_install_callback)
        Apktool.install(progress_callback=_install_callback)

        decoded_dir = os.path.join(USER_DIRECTORIES.user_cache_dir, 'decoded_tmp')

        Apktool.decode(apk, output=decoded_dir, framework_path=f'{decoded_dir}_framework', no_res=True, no_src=True, force_manifest=True)
        manifest_path = os.path.join(decoded_dir, 'AndroidManifest.xml')
        if activities:
            for activity in Manifest.get_activities(manifest_path):
                LOG.info(activity)
        if permissions:
            for permission in Manifest.get_permissions(manifest_path):
                LOG.info(permission)
        if libraries:
            for library in Manifest.get_libraries(manifest_path):
                LOG.info(library)
        if recievers:
            for reciever in Manifest.get_receivers(manifest_path):
                LOG.info('{}', reciever)
    if not os.path.isfile(apk):
        LOG.error('{} - not such file.', apk)
    if Bundle.is_bundle(apk):
        with tempfile.TemporaryDirectory() as tmp:
            apk, base = Bundle.extract(apk, tmp)
            apk = os.path.join(apk, base)
            return _parse_apk()
    _parse_apk()


@main.command(help='Manage plugins')
@click.option('--list', is_flag=True, help='List all installed and available plugins.')
@click.option('--install', required=False, help='Installs a plugin by name.')
@click.option('--remove', required=False, help='Removes an installed plugin.')
def plugins(list, install, remove):
    plugin_path = os.path.join(USER_DIRECTORIES.user_data_dir, "plugins")
    online_plugins = None

    if list:
        response = requests.get(__PLUGIN_DATA__)
        if response.status_code == 200:
            online_plugins = response.json()
        LOG.warning('INSTALLED PLUGINS')
        for plugin in os.listdir(plugin_path):
            if plugin.endswith('.py'):
                LOG.info(plugin[:-3])
        LOG.warning('AVAILABLE PLUGINS')
        if online_plugins:
            for plugin in online_plugins:
                LOG.info(plugin['name'])
                LOG.info('\tauthor: {}', plugin['author'])
                LOG.info('\tdescription: {}', plugin['description'])
                LOG.info('\tversion: {}', plugin['version'])
                LOG.info('\turl: {}', plugin['url'])

    if install:
        response = requests.get(__PLUGIN_DATA__)
        if response.status_code == 200:
            online_plugins = response.json()
            if online_plugins:
                for plugin in online_plugins:
                    if plugin['name'] == install:
                        LOG.info('Installing {} by {} version {}',
                                 plugin['name'], plugin['author'], plugin['version'])
                        response = requests.get(plugin['url'])
                        if response.status_code != 200:
                            LOG.error(
                                'Failed to download {}. Request failed with: {}', install, response.status_code)
                        out = os.path.join(plugin_path, f'{plugin["name"]}.py')
                        with open(out, 'w') as out_f:
                            out_f.write(response.text)
    if remove:
        for plugin in os.listdir(plugin_path):
            if plugin.endswith('.py'):
                name = plugin[:-3]
                if name == remove:
                    path = os.path.join(plugin_path, plugin)
                    os.remove(path)
                    LOG.info('Removed {}', path)


def start():
    plugin_folder = os.path.join(USER_DIRECTORIES.user_data_dir, 'plugins')
    if not os.path.exists(plugin_folder):
        os.makedirs(plugin_folder)
    _PluginLoader(plugin_folder)
    main()


if __name__ == '__main__':
    start()
