import subprocess
import sys

from busywork.pyproject import Group
from busywork.utils import pretty_print, error

installed_groups = []
groups_to_install = []


def install_groups(groups: list[Group]) -> None:
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
            f"Queded installation for groups: {', '.join(group.name for group in group.groups)}."
        )
    for package in group.packages:
        install(package)


def install_remaining():
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
    pretty_print(f"&6Installing package {package} through pip:")

    # Flushing stdout ensures `print` output shows before the subprocess output.
    # Speed doesn't matter here anyway so this solution is fine.
    sys.stdout.flush()

    try:
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", package],
            stderr=subprocess.STDOUT,
        )
    except subprocess.SubprocessError:
        error(f"Could not install package {package}. This is a problem with pip.")
