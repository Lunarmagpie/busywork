"""
A backend is a package installer for busywork.
"""

import abc


class Backend(abc.ABC):
    @property
    @abc.abstractmethod
    def name(self) -> str:
        ...

    @abc.abstractmethod
    def install_package(self, package: str) -> None:
        """Install package using pep 440 version"""
