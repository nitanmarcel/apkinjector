Usage
=====

::

    apkinjector [OPTIONS] COMMAND [ARGS]...
    
    Options:
    --help  Show this message and exit.

Commands:
  apk      Apk utils
  frida    Inject a frida gadget in a target apk.
  inject   Inject a shared library (.so) in a target apk.
  plugins  Manage plugins

Frida
-----

::

    Usage: python -m apkinjector frida [OPTIONS] APK

    Inject a frida gadget in a target apk.

    Options:
    --gadget TEXT     Path to custom gadget.
    --script TEXT     Inject a javascript to be loaded when the gadget starts.
    --codeshare TEXT  Same as --script but uses Frida Codeshare as the source
                        javascript.
    --arch TEXT       Architecture to inject for. If empty --adb or --gadget
                        must be specified.
    --adb             Use adb (if installed) to detect device architecture.
    --activity TEXT   Name of the activity to inject into. If unspecified, the
                        main activity will be injected.
    --output          Custom path where the patched apk should be saved.
    --force           Force delete destination directory.
    --help            Show this message and exit.

Inject
------

::

    Usage: python -m apkinjector inject [OPTIONS] APK

    Inject a shared library (*.so) in a target apk.

    Options:
    --library TEXT   Shared library (*.so) to inject.  [required]
    --include TEXT   Extra files to include in the lib folder. Can be used
                        multiple times to include more files.
    --arch TEXT      Architecture to inject for. If empty --adb or --library
                        must be specified.
    --adb            Use adb (if installed) to detect device architecture.
    --activity TEXT  Name of the activity to inject into. If unspecified, the
                        main activity will be injected.
    --output         Custom path where the patched apk should be saved.
    --force          Force delete destination directory.
    --help           Show this message and exit.

Apk utils
---------

::

    Usage: python -m apkinjector apk [OPTIONS] APK

    Apk utils

    Options:
    --activities   Gets all activities
    --permissions  Gets all permissions
    --libraries    Gets all libraries
    --recievers    Gets all receivers
    --help         Show this message and exit.