from __future__ import annotations

import importlib.metadata
import pathlib
import shutil
import sys
import sysconfig
import tarfile
import traceback

import installer
import packaging.markers
import packaging.requirements
import requests
import unearth
from installer.destinations import SchemeDictionaryDestination
from installer.sources import WheelFile

import build
import build.env
from busywork.backends.backend import Backend
from busywork.backends.pip import Pip
from busywork.utils import error, pretty_print

TMP_PATH = pathlib.Path(".busywork")


class Busywork(Backend):
    """
    Backend built with unearth
    """

    def __init__(self) -> None:
        self.pip_builder = Pip()
        self.package_finder = unearth.PackageFinder(
            index_urls=["https://pypi.org/simple/"]
        )
        self.indentation = 0

    def get_indents(self, n: int) -> str:
        return " " * (self.indentation + n) * 2

    @property
    def name(self) -> str:
        return "busywork backend"

    def indent_print(self, msg: str, arrow: bool = False) -> None:
        pretty_print(f"{self.get_indents(0)}{msg}", arrow=arrow)

    def install_package(self, package: str) -> None:
        try:
            self.install_package_unsafe(package)
        except Exception:
            traceback.print_exc()

            error(
                f"Can not install package {package}"
                "\nIf this error persists try setting busywork's backend to 'pip'"
                "in pyproject.toml."
                "\n---------------"
                "\n[tool.busywork]"
                '\nbackend = "pip"'
                "\n---------------"
            )

    def install_package_unsafe(self, package: str) -> None:
        if "@" in package:
            """
            Packaging can't parse @ in a requirement so this is yielded to pip.
            """
            self.indent_print(f"Installing '{package}' with pip", arrow=False)
            self.pip_builder.install_package(package)
            return

        requirement = packaging.requirements.Requirement(package)
        self.install_requirement(requirement)

    def install_requirement(
        self, requirement: packaging.requirements.Requirement
    ) -> None:
        if self.is_installed(requirement):
            return

        TMP_PATH.mkdir(exist_ok=True)

        matches = self.package_finder.find_best_match(requirement)

        pkg = matches.best

        if not pkg:
            error(f"Can't install package {requirement.name} because it doesn't exist.")

        # Download the package
        resp = requests.get(pkg.link.url)

        tmp_path = pathlib.Path(".busywork/") / pkg.link.filename

        with open(tmp_path, "wb") as f:
            f.write(resp.content)

        if pkg.link.filename.endswith(".whl"):
            self.install_wheel(requirement, tmp_path)
            return

        self.install_sdist(requirement, tmp_path)

    def is_installed(self, req: packaging.requirements.Requirement) -> bool:
        """
        Return `True` if a package is current installed.
        """
        try:
            if req.specifier.contains(importlib.metadata.version(req.name)):
                self.indent_print(
                    f"Skipping installing {req.name} because package is already"
                    " installed.",
                    arrow=False,
                )
                self.resolve_dependencies(req)
                return True
        except importlib.metadata.PackageNotFoundError:
            return False
        return False

    def install_wheel(
        self, req: packaging.requirements.Requirement, path: pathlib.Path
    ) -> None:
        """
        Install a wheel.
        """
        self.indent_print(
            f"Wheel found!!! Installing wheel for package {req.name}.", arrow=False
        )

        try:
            with WheelFile.open(path) as source:
                installer.install(
                    source,
                    destination=SchemeDictionaryDestination(
                        sysconfig.get_paths(),
                        interpreter=sys.executable,
                        script_kind="posix",
                    ),
                    additional_metadata={
                        "INSTALLER": b"Busywork",
                    },
                )
        except FileExistsError:
            self.indent_print(
                f"Failed to install {req.name} because it is already installed.",
                arrow=False,
            )
        path.unlink()

        self.resolve_dependencies(req)

    def install_sdist(
        self, req: packaging.requirements.Requirement, tar_path: pathlib.Path
    ) -> None:
        """
        Build a wheel then install that wheel.
        """
        self.indent_print(
            f"No wheel :(\nBuilding wheel for package {req} with build."
            " Get a cup of coffee, this might take a while.",
            arrow=False,
        )

        extract_path = pathlib.Path(".busywork/extract/")
        lib_path = extract_path / tar_path.stem.removesuffix(".tar")

        if extract_path.exists():
            shutil.rmtree(extract_path)

        with tarfile.open(tar_path) as tar:
            tar.extractall(extract_path)

        builder = build.ProjectBuilder(lib_path)

        with build.env.IsolatedEnvBuilder() as env:
            builder.python_executable = env.executable

            env.install(builder.build_system_requires)

            env.install(builder.get_requires_for_build("wheel"))
            built = builder.build("wheel", output_directory=TMP_PATH)

        tar_path.unlink()
        shutil.rmtree(extract_path)

        self.install_wheel(req, TMP_PATH / built)

    def resolve_dependencies(
        self, requirement: packaging.requirements.Requirement
    ) -> None:
        deps = importlib.metadata.requires(requirement.name)

        if not deps:
            return

        dependencies: list[packaging.requirements.Requirement] = [
            packaging.requirements.Requirement(dep) for dep in deps
        ]

        dep_queue = []

        for dep in dependencies:
            # if dep.marker and dep.marker not in extra_markers:
            # return
            if not dep.marker:
                dep_queue.append(dep)
                continue

            try:
                # If the marker can evaluate without extras, we say it can be installed.
                should_install = dep.marker.evaluate({})
            except packaging.markers.UndefinedEnvironmentName:
                # Otherwise we need to check if it can be evaluated with any of the extras.
                should_install = any(
                    dep.marker.evaluate({"extra": extra})
                    for extra in requirement.extras
                )

            if should_install:
                dep_queue.append(dep)
                continue

        if not dep_queue:
            return

        self.indent_print(
            f"Installing dependencies for {requirement.name}.", arrow=False
        )

        self.indentation += 1

        for dep in dep_queue:
            self.install_requirement(dep)

        self.indentation -= 1
