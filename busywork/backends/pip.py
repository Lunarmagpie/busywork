"""
The pip backend.
"""
import subprocess
import sys

from busywork.backends.backend import Backend
from busywork.utils import error


class Pip(Backend):
    @property
    def name(self) -> str:
        return "pip"

    def install_package(self, package: str) -> None:
        # Flushing stdout ensures `print` output shows before the subprocess output.
        # Speed doesn't matter here anyway so this solution is fine.
        sys.stdout.flush()

        output = subprocess.run(
            [sys.executable, "-m", "pip", "install", package],
            stderr=subprocess.STDOUT,
        )

        if output.returncode != 0:
            error(
                f"Could not install package {package} because there was a problem"
                " with pip."
            )
