import nox


def session(*groups: str):
    def inner(func):
        @nox.session(name=func.__name__)
        def session(session: nox.Session):
            session.install("busywork")
            for group in groups:
                session.run("busywork", "install", "-g", group)
            func(session)

        return session

    return inner


@session("typing")
def mypy(session: nox.Session) -> None:
    session.run("mypy", "busywork")


@session("linting")
def format(session: nox.Session) -> None:
    session.run("black", ".")
    session.run("isort", ".")


@session("linting")
def lint(session: nox.Session) -> None:
    session.run("black", ".", "--check")
    session.run("isort", ".", "--check")
