from apkinjector import LOG, DEPENDENCIES
from apkinjector.plugins import main
import click
import subprocess


# Define a new command. It uses click under the hood. See more at https://click.palletsprojects.com/en/8.1.x/
@main.command(help='Prints hello world to the console.')
def hello_world():
    LOG.info('Hello World')  # prints info
    LOG.warning("Hello World")  # prints warning
    LOG.error('Hello World')  # prints error and calls sys.exit(1)


@main.command(help='Calls uname')
@click.option('--a', is_flag=True, help='Calls uname with the argument -a')
def uname(a):
    # Adds a new dependency `uname`.
    DEPENDENCIES.add_dependency('uname', required=True)
    if DEPENDENCIES.uname:  # Checks if the depedency `uname` is installed.
        if a:
            process = subprocess.run(
                f'uname -a', shell=True, capture_output=True, text=True)
        else:
            process = subprocess.run(
                f'uname', shell=True, capture_output=True, text=True)
        # Outputs the output of uname to console
        LOG.info('uname result: {}', process.stdout)
