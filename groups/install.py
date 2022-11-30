import subprocess
import sys

from dahlia import dprint

from groups.pyproject import Group

INSTALLED_GROUPS = []
GROUPS_TO_INSTALL = []


def install_groups(groups: list[Group]) -> None:
    for group in groups:
        install_group(group)


def install_group(group: Group) -> None:
    if group in INSTALLED_GROUPS:
        return
    dprint(f"&eInstalling group {group.name}:")
    INSTALLED_GROUPS.append(group)
    for package in group.packages:
        install(package)
    if group.groups:
        GROUPS_TO_INSTALL.extend(group.groups)
        print(
            f"Queded installation for groups: {', '.join(group.name for group in group.groups)}:"
        )


def install_remaining():
    for group in GROUPS_TO_INSTALL:
        install_group(group)
    dprint("&aPackages succesfully installed!")


def install(package: str) -> None:
    dprint(f"&gInstalling package {package}:")
    subprocess.check_call(
        [sys.executable, "-m", "pip", "install", package],
    )
