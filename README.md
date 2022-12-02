# Busywork

Dependency group support using `pyproject.toml`. Dependency groups are dependencies
that are used in development that the user does not need to install, such as black
or mypy.


## Usage

Add this to your pyproject.toml
```toml
[tool.busywork.groups.linting]
# PEP 440 dependency specification.
requires = ["black", "isort"]

[tool.busywork.groups.typing]
requires = ["mypy", "types-toml"]

[tool.busywork.groups.dev]
# Nested groups
requires = ["nox"]
requires-groups = ["linting", "typing"]
```

Now install the group:

`busywork install --group group-name`

Groups can be separated by a comma for multiple groups.

`busywork install --group group-one,group-two,group-three`

Other options:
```sh
busywork install --all  # Install all dependency groups.
busywork install --dependencies  # Install the current project's dependencies.
busywork install --this  # Install the current project. This is the equivalent to `pip install .`

# arguments can also be combined, for example:
busywork install --this --all  # Install the current project and all dependency groups.
```

## Credits

- Dependency groups are inspired by poetry.
- The CLI visuals are inspired by nox.
