import subprocess
import sys

import dahlia

from busywork.pyproject import Group

installed_groups = []
groups_to_install = []


def install_groups(groups: list[Group]) -> None:
    for group in groups:
        install_group(group)


def install_group(group: Group) -> None:
    if group in installed_groups:
        return
    dahlia.dprint(f"&eInstalling group {group.name}:")
    installed_groups.append(group)
    if group.groups:
        groups_to_install.extend(group.groups)
        print(
            f"Queded installation for groups: {', '.join(group.name for group in group.groups)}:"
        )
    for package in group.packages:
        install(package)


def install_remaining():
    for group in groups_to_install:
        install_group(group)
    dahlia.dprint("&aPackages succesfully installed!")


def install(package: str) -> None:
    dahlia.dprint(f"&gInstalling package {package}:")
    subprocess.check_call(
        [sys.executable, "-m", "pip", "install", package],
    )
