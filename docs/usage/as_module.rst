Usage as a module
=================

.. code-block:: python

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