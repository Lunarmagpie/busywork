import argparse
import sys

from busywork.install import install, install_group, install_groups, install_remaining
from busywork.pyproject import META
from busywork.utils import error, pretty_print


class CommandLine:
    def __init__(self) -> None:
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
                f"`{sys.argv[1]}` is not a valid subcommand."
                " Type `busywork -h` to see the help menu."
            )

    def install(self) -> None:
        parser = argparse.ArgumentParser(
            prog="Groups",
            description="Install dependency groups.",
        )

        parser.add_argument(
            "-a",
            "--all",
            action="store_true",
            help="Install all groups. Multiple groups can be separated by commas.",
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
            install_groups(META.groups.values())

        if getattr(args, "group", None):
            found_flag = True

            if "," in args.group:
                groups = args.group.split(",")
            else:
                groups = [args.group]

            for group in groups:
                if group not in META.groups:
                    error(
                        f'Can not install group "{group}" because group is not defined.'
                    )

            install_groups(META.groups[group] for group in groups)

        if getattr(args, "this", None):
            found_flag = True
            install(".")

        if getattr(args, "dependencies", None):
            found_flag = True
            install_group(META.project_dependencies)

        if found_flag:
            install_remaining()
        else:
            error("No group provided.")

        pretty_print("&aPackages successfully installed!")
