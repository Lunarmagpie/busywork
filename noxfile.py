import nox

import busywork


@busywork.session("typing")
def mypy(session: nox.Session) -> None:
    session.run("mypy", "busywork")


@busywork.session("linting")
def format(session: nox.Session) -> None:
    session.run("black", ".")
    session.run("isort", ".")


@busywork.session("linting")
def lint(session: nox.Session) -> None:
    session.run("black", ".", "--check")
    session.run("isort", ".", "--check")
