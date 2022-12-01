import argparse
import sys

from busywork.install import install_group, install_groups, install_remaining
from busywork.pyproject import Metadata
from busywork.utils import error


class CommandLine:
    def __init__(self) -> None:
        self.meta = Metadata()

        if len(sys.argv) <= 1:
            error("Expected at least one argument.")

        if sys.argv[1] == "-h":
            print(
                # fmt: off
                "usage: busywork [command]",
                "\n"
                "\ncommand must be one of the following:"
                "\n`install` - Install a dependency group."
                # fmt: on
            )
            sys.exit(0)

        if hasattr(self, sys.argv[1]):
            getattr(self, sys.argv[1])()
        else:
            error(
                f"`{sys.argv[1]}` is not a valid subcommand. Type `busywork -h` to see the help menu."
            )

    def install(self):
        parser = argparse.ArgumentParser(
            prog="Groups",
            description="Install dependency groups.",
        )

        parser.add_argument(
            "-a", "--all", action="store_true", help="Install all groups."
        )
        parser.add_argument("-g", "--group", help="Install a group.")

        args = parser.parse_args(sys.argv[2:])

        if getattr(args, "all", False):
            install_groups(self.meta.groups.values())
            install_remaining()

        elif getattr(args, "group", None):
            try:
                install_group(self.meta.groups[args.group])
            except KeyError:
                error(
                    f'Can not install group "{args.group}" because group is not defined.'
                )
            install_remaining()

        else:
            error("No group provided.")
