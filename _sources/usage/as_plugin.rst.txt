Usage as a plugin
=================

.. code-block:: python

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