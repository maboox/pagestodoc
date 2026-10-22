"""Install pinned dependencies in a project-local environment on first launch."""

import os
import subprocess
import sys
import venv
from pathlib import Path


def main():
    if sys.version_info < (3, 10):  # noqa: UP036 -- launcher also runs before dependencies are installed
        raise SystemExit("Python 3.10 or newer is required.")
    root = Path(__file__).resolve().parent
    environment = root / ".venv"
    python = environment / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
    try:
        if not python.is_file():
            print("Creating the local Python environment…", flush=True)
            venv.EnvBuilder(with_pip=True).create(environment)
        check = (
            "from importlib.metadata import version; from pathlib import Path; "
            "assert all(version(name)==expected for name,expected in "
            "(line.strip().split('==') for line in Path('requirements.txt').read_text().splitlines() if line.strip()))"
        )
        installed = subprocess.run(
            [str(python), "-c", check],
            cwd=root,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False,
        )
        if installed.returncode:
            print("Installing pinned dependencies from PyPI (first launch or update)…", flush=True)
            subprocess.run(
                [
                    str(python),
                    "-m",
                    "pip",
                    "install",
                    "--disable-pip-version-check",
                    "--no-input",
                    "-r",
                    str(root / "requirements.txt"),
                ],
                cwd=root,
                check=True,
            )
    except (OSError, subprocess.CalledProcessError) as exc:
        raise SystemExit(
            "Setup failed. Check internet access, Python's venv/pip support, and folder permissions."
        ) from exc
    os.chdir(root)
    os.execv(str(python), [str(python), str(root / "app.py"), "--open", *sys.argv[1:]])


if __name__ == "__main__":
    main()
