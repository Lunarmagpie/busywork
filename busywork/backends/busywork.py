import unearth
import installer
import build
import requests
import pathlib
import tarfile

import sys
import shutil
import sysconfig

from installer.destinations import SchemeDictionaryDestination
from installer.sources import WheelFile

from busywork.utils import pretty_print
from busywork.backends.backend import Backend


class Busywork(Backend):
    """
    Backend built with unearth
    """

    def __init__(self) -> None:
        self.package_finder = unearth.PackageFinder(
            index_urls=["https://pypi.org/simple/"]
        )

    @property
    def name(self) -> str:
        return "busywork backend"

    def install_package(self, package: str) -> None:
        matches = self.package_finder.find_best_match(package)

        pkg = matches.best

        if not pkg:
            raise Exception

        # Download the package
        resp = requests.get(matches.best.link.url)

        tmp_path = pathlib.Path(".busywork/") / matches.best.link.filename

        with open(tmp_path, "wb") as f:
            f.write(resp.content)

        if matches.best.link.filename.endswith("*.whl"):
            self.install_wheel(pkg, tmp_path)

        self.install_sdist(pkg, tmp_path)

    def install_wheel(self, pkg: unearth.Package, path: pathlib.Path):
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

    def install_sdist(self, pkg: unearth.Package, zip_path: pathlib.Path):
        extract_path = pathlib.Path(f".busywork/extract/")
        wheel_path = extract_path / zip_path.stem.removesuffix(".tar")

        if extract_path.exists():
            shutil.rmtree(extract_path)

        with tarfile.open(zip_path) as tar:
            tar.extractall(extract_path)

        builder = build.ProjectBuilder(wheel_path, python_executable=sys.executable)

        builder.build("wheel", output_directory=pathlib.Path(".busywork"))

        self.install_wheel(pkg, wheel_path)
