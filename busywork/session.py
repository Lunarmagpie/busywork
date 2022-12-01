from __future__ import annotations

import typing as t

if t.TYPE_CHECKING:
    import nox


def session(
    *groups: str,
    **kwargs: t.Any,
) -> t.Callable[[t.Callable[[nox.Session], t.Any]], t.Callable[[nox.Session], None]]:
    """
    Nox session that can be used to install busywork groups.
    `kwargs` are passed into the `@nox.session` decorator.
    """
    try:
        import nox
    except ImportError:
        raise ModuleNotFoundError("`nox` must be installed to use `busywork.session`")

    def inner(func) -> t.Callable[[nox.Session], t.Any]:
        @nox.session(name=kwargs.get("name", func.__name__), **kwargs)
        def session(session: nox.Session) -> None:
            session.install("busywork")
            session.run("busywork", "install", "-g", ",".join(groups))
            func(session)

        return session

    return inner
