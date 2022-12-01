import argparse
import sys

from busywork.install import install_group, install_groups, install_remaining, install
from busywork.pyproject import Metadata
from busywork.utils import error
import dahlia


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
        parser.add_argument(
            "-t", "--this", action="store_true", help="Install the current project."
        )
        parser.add_argument(
            "-d",
            "--dependencies",
            action="store_true",
            help="Install the current project's dependencies.",
        )
        parser.add_argument("-g", "--group", help="Install a group.")

        args = parser.parse_args(sys.argv[2:])

        found_flag = False

        if getattr(args, "all", None):
            found_flag = True
            install_groups(self.meta.groups.values())

        if getattr(args, "group", None):
            found_flag = True
            try:
                install_group(self.meta.groups[args.group])
            except KeyError:
                error(
                    f'Can not install group "{args.group}" because group is not defined.'
                )

        if getattr(args, "this", None):
            found_flag = True
            install(".")

        if getattr(args, "dependencies", None):
            found_flag = True
            install_group(self.meta.dependency_group)

        if found_flag:
            install_remaining()
        else:
            error("No group provided.")

        dahlia.dprint("&aPackages succesfully installed!")
