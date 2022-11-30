import sys
import typing as t

import dahlia


def error(msg: str) -> t.NoReturn:
    dahlia.dprint(f"&c{msg}")
    sys.exit(1)
