import os
import shutil
from dataclasses import dataclass
from typing import Callable, Optional, Union


@dataclass
class Dependency:
    name: str
    path: str
    required: bool


class DependenciesManager:
    """
    This class manages system-level dependencies by tracking them,
    and their status within a provided directory.
    """

    def __init__(self, dependencies_directory: str) -> None:
        """
        Initializes the Dependencies Manager.

        :param dependencies_directory: The directory containing the dependencies.
        "type dependencies_directory: str
        """
        self.dependencies_directory = dependencies_directory
        self.dependencies = []  # List to store the tracked dependencies.

    def add_dependency(self, name: str, path: str = None, required: bool = False, fallback: Optional[Callable] = None, fallback_args: tuple = None) -> Dependency:
        """
        Adds a new dependency to the tracked list.

        :param name: The name of the dependency.
        :type name: str
        :param path: Path to existing dependency. If left None, it will detect the system dependency or call fallback function, defaults to None.
        :type path: str, optional
        :param required: Indicates if the dependency is required, defaults to False.
        :type required: bool
        :param fallback: The fallback function if the dependency is not found, defaults to None.
        :type fallback: Callable, optional
        :param fallback_args: Arguments to be passed to the fallback function, defaults to ().
        :type fallback_args: tuple, optional
        :return: The newly added dependency.
        :rtype: Dependency
        """
        path = path or shutil.which(name)
        if not path or not os.path.isfile(path):
            if callable(fallback):
                if fallback_args and isinstance(fallback_args, (tuple, list)):
                    path = fallback(*fallback_args)
                elif fallback_args:
                    path = fallback(fallback_args)
        dependency = Dependency(name, path, required)
        self.dependencies.append(dependency)
        return dependency

    def get_dependency(self, name: str) -> Dependency:
        """
        Retrieves a tracked dependency by name.

        :param name: The name of the dependency.
        :type name: str
        :return: The corresponding Dependency object if it is found, None otherwise.
        :rtype: Dependency
        """
        dependency = [
            x for x in self.dependencies if x.path is not None and x.name == name]
        if dependency:
            return dependency[0]
        return None

    def has_missing_required_dependency(self) -> bool:
        """
        Checks if there is any required dependency missing.

        :return: True if a required dependency is missing, False otherwise.
        :rtype: bool
        """
        dependency = [
            x for x in self.dependencies if x.path is None and x.required]
        if dependency:
            return True
        return False

    def __getattr__(self, name: str) -> str:
        """
        Overwrites the default Python attribute getter (__getattr__).
        It allows us to get a dependency as an object attribute.

        :param name: The name of the attribute (constructed from the dependency's name).
        :type name: str
        :return: Path to dependency executable.
        :rtype: str
        """
        name = name.replace('_', '-')
        dependency = self.get_dependency(name)
        if dependency:
            return dependency.path
        return None
