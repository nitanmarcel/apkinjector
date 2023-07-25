import os
import shutil
from typing import List

from elftools.elf.elffile import ELFFile

from .arch import ARCH
from .utils import arch_to_abi


class Injector:
    @staticmethod
    def inject_library(source: str, unpack_path: str, smali_path: str = None, extra_files: List[str] = None) ->:
        """Inject library into unpacked apk

        Args:
            source (str): Path to shared library to inject.
            unpack_path (str): Path to apktool unpacked apk.
            smali_path (str, optional): _description_. Path to smali file to inject into. Leave empty to skip this step
            extra_files (List[str], optional): _description_. Extra files to copy over the the apk lib/ folder

        Returns:
            bool: If the injection was succesful or not.
        """
        lib, ext = os.path.basename(source).rsplit('.', 1)
        lib = lib.split('lib', 1)[-1]
        lines = []
        injected = False
        if smali_path and not os.path.isfile(smali_path):
            return injected

        abi = None

        with open(source, 'rb') as libfile:
            elffile = ELFFile(libfile)
            arch = elffile.get_machine_arch()
            if arch.lower() in ['aarch64', 'arm64']:
                arch = ARCH.ARM64
            if arch.lower() in ['x64']:
                return ARCH.X64
            abi = arch_to_abi(arch.lower())

        path = os.path.join(unpack_path, 'lib', abi)
        if not os.path.isdir(path):
            os.makedirs(path)
        paths = []
        paths.append(source)
        if extra_files:
            paths.extend(extra_files)
        for file in paths:
            name = os.path.basename(file)
            dest = os.path.join(path, name)
            if os.path.isfile(dest):
                os.remove(dest)
            shutil.copyfile(file, dest)

        injected = not bool(smali_path)
        if smali_path:
            with open(smali_path, 'r') as smali:
                lines = smali.readlines()
            matches = []
            for line in lines:
                if 'const-string v0, "{}"\n'.format(lib) in line:
                    matches.append(line)
                if matches and 'invoke-static {v0}, Ljava/lang/System;->loadLibrary(Ljava/lang/String;)V\n' in line:
                    matches.append(line)
            if len(matches) >= 2:
                return True
            for line in lines:
                if line.startswith('.method public constructor <init>()V') or line.startswith('.method static constructor <clinit>()V'):
                    index = lines.index(line)
                    if lines[index + 1].startswith('    .locals'):
                        lines.insert(
                            index + 2, '    const-string v0, "{}"\n'.format(lib))
                        lines.insert(
                            index + 3, '    invoke-static {v0}, Ljava/lang/System;->loadLibrary(Ljava/lang/String;)V\n')
                        injected = True
                        break
                    else:
                        lines.insert(
                            index + 1, '    const-string v0, "{}"\n'.format(lib))
                        lines.insert(
                            index + 2, '    invoke-static {v0}, Ljava/lang/System;->loadLibrary(Ljava/lang/String;)V\n')
                        injected = True
                        break
            with open(smali_path, 'w') as smali:
                smali.writelines(lines)
        return injected
