from __future__ import annotations

import dataclasses
import typing as t

import tomli


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

        groups: dict[str, t.Any] = data["tool"]["busywork"]["groups"]

        self.groups = {name: Group.from_str(name, groups) for name in groups.keys()}
