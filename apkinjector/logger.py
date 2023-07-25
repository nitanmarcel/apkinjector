import sys

import click

from typing import List, Tuple, Union


class ApkInjectorLogger:
    """
    Fstring like logging. e.g: log.info('Hello {}', 'World')
    """
    def __init__(self, name : str):
        """
        Initializes the logger.

        :param name: Name of the logger.
        :type name: str
        """
        self.__name__ = name

    def info(self, message: str, *args : Union[Tuple[str], List[str]]):
        """
        Prints info log message in green.

        :param message: Message to print.
        :type message: str
        """
        message = message.format(*args)
        click.echo(click.style(f'[+] {self.__name__} - {message}', fg='green'))

    def warning(self, message: str, *args : Union[Tuple[str], List[str]]):
        """
        Prints warning log message in yellow.

        :param message: Message to print.
        :type message: str
        """
        message = message.format(*args)
        click.echo(click.style(
            f'[!] {self.__name__} - {message}', fg='yellow'))

    def error(self, message: str, *args : Union[Tuple[str], List[str]]):
        """
        Prints error message in red and calls sys.exit(1).

        :param message: Message to print.
        :type message: str
        """
        message = message.format(*args)
        click.echo(click.style(f'[*] {self.__name__} - {message}', fg='red'))
        sys.exit(1)
