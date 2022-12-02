import typing as t

from busywork.pyproject import META, Group
from busywork.utils import pretty_print

installed_groups = []
groups_to_install = []


def install_groups(groups: t.Iterable[Group]) -> None:
    for group in groups:
        install_group(group)


def install_group(group: Group) -> None:
    if group in installed_groups:
        return
    pretty_print(f"&eInstalling group {group.name}:")
    installed_groups.append(group)
    if group.groups:
        groups_to_install.extend(group.groups)
        pretty_print(
            "Queded installation for groups:"
            f" {', '.join(group.name for group in group.groups)}."
        )
    for package in group.packages:
        install(package)


def install_remaining() -> None:
    """
    Install all dependency groups qeued to install if there are any.
    """
    if not groups_to_install:
        return
    for group in groups_to_install:
        install_group(group)
        groups_to_install.remove(group)
    install_remaining()


def install(package: str) -> None:
    pretty_print(f"&6Installing package {package} with {META.backend.name}:")

    META.backend.install_package(package)
