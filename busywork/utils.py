import sys
import os
import typing as t

import dahlia

__all__: t.Sequence = ("error", "pretty_print")


def error(msg: str) -> t.NoReturn:
    pretty_print(f"&cError: {msg}")
    sys.exit(1)


def pretty_print(msg: str):
    dahlia.dprint(f"&3busywork > &r{msg}", depth=dahlia.Depth.TTY)
