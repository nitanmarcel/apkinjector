# APK Injector

Pluginable tool to automate injection of libraries in apks, with support for unpack, repack, and bundles.

- [APK Injector](#apk-injector)
    - [Features](#features)
    - [Installation](#installation)
    - [Usage](#usage)
      - [Frida](#frida)
      - [Inject](#inject)
      - [Apk utils](#apk-utils)
      - [Plugins](#plugins)
    - [Using as a module](#using-as-a-module)
    - [Usage as a plugin](#usage-as-a-plugin)

### Features
- Insert libraries and load them when an activity starts.
- Frida support with support to load frida scripts either from disc or codeshare.
- Bundle support. Apks exported from SAI or XApks downloaded from apkpure.
- Plugins support. Check plugins/plugins.json and plugin_example.py

### Installation
`pip3 install apkinjector`

### Usage
```
apkinjector [OPTIONS] COMMAND [ARGS]...

Options:
  --help  Show this message and exit.

Commands:
  apk      Apk utils
  frida    Inject a frida gadget in a target apk.
  inject   Inject a shared library (*.so) in a target apk.
  plugins  Manage plugins
```


#### Frida
```
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
```

#### Inject
```
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
```

#### Apk utils
```
Usage: python -m apkinjector apk [OPTIONS] APK

  Apk utils

Options:
  --activities   Gets all activities
  --permissions  Gets all permissions
  --libraries    Gets all libraries
  --recievers    Gets all receivers
  --help         Show this message and exit.
```

#### Plugins
```
Usage: python -m apkinjector plugins [OPTIONS]

  Manage plugins

Options:
  --list          List all installed and available plugins.
  --install TEXT  Installs a plugin by name.
  --remove TEXT   Removes an installed plugin.
  --help          Show this message and exit.
```


### Using as a module

```python
from apkinjector import LOG


LOG.info("This has been printed using apkinjector logging")


# Also comes with runners for apktool, uber-apk-signer, etc/

from apkinjector.apktool import ApkTool

from apkinjector.uber_apk_signer import UberApkSigner

# Automatically download and setup apktool.
ApkTool.install()

# Decompile apk
ApkTool.decode(...)

# Automatically download and setup uber-apk-signer
UberApkSigner.install()

# Sign apk
UberApkSigner.sign(...)


# Check if a dependency is in path

from apkinjector import DEPENDENCIES_MANAGER

# Add a new dependency
java = DEPENDENCIES_MANAGER.add_dependency('java', required=True) # Return Depedency(name, path, required)

# Check if a dependency is path
# Returns the path to the binary if found, if not returns None
# See apkpatcher/apkpatcher to see how dependencies are automatically handled
in_path = DEPENDENCIES_MANAGER.java
```

### Usage as a plugin

```python

# Can use the same methods as a it would been included in a separate module.

from apkinjector import LOG

# Adding a new command to the `apkinjector` application:

from apkinjector.plugins import main

# Define a new command. It uses click under the hood. See more at https://click.palletsprojects.com/en/8.1.x/
# Check plugins/plugin_example.py for a full example.
@main.command(help='Prints hello world to the console.')
def hello_world():
    LOG.info('Hello World')  # prints info
    LOG.warning("Hello World")  # prints warning
    LOG.error('Hello World')  # prints error and calls sys.exit(1)

# This will be usable with `apkinjector hello_world`
# 
# apkinjector hello-world --help
# Usage: python -m apkinjector hello-world [OPTIONS]

#   Prints hello world to the console.

# Options:
#   --help  Show this message and exit. 
```