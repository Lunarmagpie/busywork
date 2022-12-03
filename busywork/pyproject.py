from __future__ import annotations

import dataclasses
import typing as t

import tomli

from busywork.backends import Backend, Busywork, Pip
from busywork.utils import error


@dataclasses.dataclass
class Group:
    name: str
    groups: list[Group]
    packages: list[str]

    @classmethod
    def from_str(cls, name: str, groups: dict[str, t.Any]) -> Group:

        this_group = groups[name]

        subgroups = [
            Group.from_str(name, groups)
            for name in this_group.get("requires-groups", [])
        ]

        return Group(
            name=name, groups=subgroups, packages=this_group.get("requires", [])
        )


class Metadata:
    def __init__(self) -> None:
        with open("pyproject.toml", "rb") as f:
            data = tomli.load(f)

        try:
            tool_busywork: dict[str, t.Any] = data["tool"]["busywork"]
        except KeyError:
            error("Expected [tool.busywork] section in pyproject.toml.")

        groups: dict[str, t.Any] = tool_busywork["groups"]

        self.groups = {name: Group.from_str(name, groups) for name in groups.keys()}

        self.project_dependencies = Group(
            name="project dependencies",
            groups=[],
            packages=data["project"].get("dependencies", []),
        )

        backend = tool_busywork.get("backend", "busywork")

        if backend not in {"busywork", "pip"}:
            error('tool.busywork.backend must be "busywork" or "pip"')

        self.backend: Backend = {"busywork": Busywork, "pip": Pip}[backend]()


META = Metadata()
