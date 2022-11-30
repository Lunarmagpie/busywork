import argparse

from groups.install import install_group, install_groups, install_remaining
from groups.pyproject import Metadata
from groups.utils import error


def main():
    parser = argparse.ArgumentParser(
        prog="Groups",
        description="Install dependency groups.",
        epilog="Text at the bottom of help",
    )

    parser.add_argument("-a", "--all", action="store_true", help="Install all groups.")
    parser.add_argument("-g", "--group", help="Install a group.")

    args = parser.parse_args()

    meta = Metadata()

    if getattr(args, "all", False):
        install_groups(meta.groups.values())
        install_remaining()

    elif getattr(args, "group", None):
        try:
            install_group(meta.groups[args.group])
        except KeyError:
            error(f'Can not install group "{args.group}" because group is not defined.')
        install_remaining()

    else:
        error("No group provided.")


if __name__ == "__main__":
    main()
