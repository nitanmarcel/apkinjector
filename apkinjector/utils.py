from typing import Union

from .arch import ARCH


def abi_to_arch(abi: str) -> Union[ARCH, None]:
    """Convert abi string to architecture

    Args:
        abi (str): Abi string

    Returns:
        Union[ARCH, None]: Converted abi to apkinjector.arch.Arch or None if the abi is not recognized.
    """
    mappings = {
        'armeabi-v7a': ARCH.ARM,
        'arm64_v8a': ARCH.ARM64,
        'x86': ARCH.X86,
        'x86_64': ARCH.X64
    }
    if abi in mappings.keys():
        return mappings[abi]
    return None


def arch_to_abi(arch: ARCH) -> Union[str, None]:
    """Convert apkinjector.arch.ARCH string to abi

    Args:
        arch (str): apkinjector.arch.ARCH

    Returns:
        Union[ARCH, None]: Converted apkinjector.arch.ARCH to abi string or None if the apkinjector.arch.ARCH is not recognized.
    """
    mappings = {
        ARCH.ARM: 'armeabi-v7a',
        ARCH.ARM64: 'arm64-v8a',
        ARCH.X86: 'x86',
        ARCH.X64: 'x86_64'
    }
    if arch in mappings.keys():
        return mappings[arch]
    return None
