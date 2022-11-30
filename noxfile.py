import nox


@nox.session
def mypy(session: nox.Session) -> None:
    session.run("groups", "-g", "typing")
    session.run("mypy", "groups")


@nox.session(name="format")
def format(session: nox.Session) -> None:
    session.run("groups", "-g", "linting")
    session.run("black", ".")
    session.run("isort", ".")


@nox.session
def lint(session: nox.Session) -> None:
    session.run("groups", "-g", "linting")
    session.run("black", ".", "--check")
    session.run("isort", ".", "--check")
