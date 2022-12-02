import sys
import typing as t

import dahlia

__all__: t.Sequence[str] = ("error", "pretty_print")


def error(msg: str) -> t.NoReturn:
    pretty_print(f"&cError: {msg}")
    sys.exit(1)


def pretty_print(msg: str, arrow: bool = True) -> None:
    dahlia.dprint(f"{'&3busywork > &r' if arrow else ''}{msg}", depth=dahlia.Depth.TTY)
