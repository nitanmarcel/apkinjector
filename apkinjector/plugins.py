import importlib.util
import os

import click
import requests


@click.group()
@click.version_option()
@click.pass_context
def main(ctx):
    """
    Entry point for apkinjector application. Use as decorator @main.command() to add new terminal commands: https://click.palletsprojects.com/en/8.1.x
    """
    pass


class _PluginLoader:
    def __init__(self, plugin_folder: str) -> None:
        self.plugin_folder = plugin_folder
        self.plugins = self.load_plugins()

    def load_plugins(self):
        plugins = {}
        for filename in os.listdir(self.plugin_folder):
            if filename.endswith('.py'):
                module_name = filename[:-3]
                plugin_module = self.import_module_from_file(
                    os.path.join(self.plugin_folder, filename))
                plugins[module_name] = plugin_module
        return plugins

    def import_module_from_file(self, full_path):
        module_spec = importlib.util.spec_from_file_location(
            os.path.basename(full_path), full_path)
        module = importlib.util.module_from_spec(module_spec)
        module_spec.loader.exec_module(module)
        return module
