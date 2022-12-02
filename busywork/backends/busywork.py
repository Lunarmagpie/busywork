import pathlib
import shutil
import sys
import sysconfig
import tarfile

import installer
import packaging.requirements
import requests
import unearth
from installer.destinations import SchemeDictionaryDestination
from installer.sources import WheelFile

import build
import build.env
from busywork.backends.backend import Backend
from busywork.backends.pip import Pip
from busywork.utils import pretty_print

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

    @property
    def name(self) -> str:
        return "busywork backend"

    def install_package(self, package: str) -> None:
        if "@" in package:
            """
            Packaging can't parse @ in a requirement so this is yielded to pip.
            """
            spaceless_req = "".join(package.split(" "))
            pip_req = spaceless_req.removeprefix("pip@")

            pretty_print(f"Installing '{pip_req}' with pip")
            self.pip_builder.install_package(pip_req)
            return

        requirement = packaging.requirements.Requirement(package)

        if self.is_installed(requirement):
            pretty_print(
                f"Skipping installing {requirement.name} because package is already"
                " installed.",
                arrow=False,
            )
            return

        TMP_PATH.mkdir(exist_ok=True)

        matches = self.package_finder.find_best_match(requirement)

        pkg = matches.best

        if not pkg:
            raise Exception

        # Download the package
        resp = requests.get(pkg.link.url)

        tmp_path = pathlib.Path(".busywork/") / pkg.link.filename

        with open(tmp_path, "wb") as f:
            f.write(resp.content)

        if pkg.link.filename.endswith(".whl"):
            self.install_wheel(pkg, tmp_path)
            return

        self.install_sdist(pkg, tmp_path)

    def is_installed(self, req: packaging.requirements.Requirement) -> bool:
        """
        Return `True` if a package is current installed.
        """
        for path in sys.path:
            for dir in pathlib.Path(path).glob("*.dist-info"):
                with (dir / "METADATA").open() as f:
                    lines = f.read().splitlines()

                    name = lines[1].split(": ")[1]
                    version = lines[2].split(": ")[1]

                    if name == req.name and req.specifier.contains(version):
                        return True

        return False

    def install_wheel(self, pkg: unearth.Package, path: pathlib.Path) -> None:
        """
        Install a wheel.
        """
        pretty_print(
            f"Wheel found!!! Installing wheel for package {pkg.name}.", arrow=False
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
            pretty_print(
                f"Skipping installing {pkg.name} because it is already installed."
            )

        path.unlink()

    def install_sdist(self, pkg: unearth.Package, tar_path: pathlib.Path) -> None:
        """
        Build a wheel then install that wheel.
        """
        pretty_print(
            f"No wheel :(\nBuilding wheel for package {pkg.name} with build."
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

        self.install_wheel(pkg, TMP_PATH / built)
