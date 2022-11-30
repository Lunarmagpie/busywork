# Groups

Dependency group support using `pyproject.toml`. Dependency groups are dependencies
that are used in development that the user does not need to install, such as black
or mypy.


## Usage

Add this to your pyproject.toml
```toml
[tool.groups.linting]
# PEP 440 dependency specification.
requires = ["black", "isort"]

[tool.groups.typing]
requires = ["mypy", "types-toml"]

[tool.groups.dev]
# Nested groups
requires = ["nox"]
requires-groups = ["linting", "typing"]
```

Now install the group:

`groups -g group-name`

Or all the groups:

`groups --all`
