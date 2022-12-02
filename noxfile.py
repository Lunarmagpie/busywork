import nox

FORMAT_PATHS = ["busywork", "noxfile.py"]
SPELLCHECK_PATHS = ["busywork", "noxfile.py", "README.md", "pyproject.toml"]
TYPED_PATHS = ["busywork"]


def session(*groups: str):
    def inner(func):
        @nox.session(name=func.__name__)
        def session(session: nox.Session):
            session.run("pip", "install", "--editable", ".")
            session.run("busywork", "install", "-g", ",".join(groups))
            func(session)

        return session

    return inner


@session("typing")
def mypy(session: nox.Session) -> None:
    session.run("mypy", *TYPED_PATHS)


@session("linting")
def format(session: nox.Session) -> None:
    session.run("black", *FORMAT_PATHS)
    session.run("isort", *FORMAT_PATHS)


@session("linting")
def lint(session: nox.Session) -> None:
    session.run("ruff", *FORMAT_PATHS)
    session.run("black", *FORMAT_PATHS, "--check")
    session.run("isort", ".", "--check")
    session.run("codespell", *SPELLCHECK_PATHS)
