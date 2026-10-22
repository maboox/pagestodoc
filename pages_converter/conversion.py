"""Invoke a private LibreOffice profile, validate input, and bound execution."""

import os
import platform
import shutil
import subprocess
import tempfile
import time
import zipfile
from pathlib import Path


class ConversionError(Exception):
    pass


class Cancelled(Exception):
    pass


def find_soffice():
    override = os.environ.get("PAGES_SOFFICE")
    if override:
        return str(Path(override).resolve()) if Path(override).is_file() else None
    found = shutil.which("soffice.com") or shutil.which("soffice") or shutil.which("libreoffice")
    if found:
        return found
    if platform.system() == "Windows":
        for variable, default in (
            ("PROGRAMFILES", "C:/Program Files"),
            ("PROGRAMFILES(X86)", "C:/Program Files (x86)"),
        ):
            for binary in ("soffice.com", "soffice.exe"):
                candidate = Path(os.environ.get(variable, default)) / "LibreOffice/program" / binary
                if candidate.is_file():
                    return str(candidate)
    if platform.system() == "Darwin":
        candidate = Path("/Applications/LibreOffice.app/Contents/MacOS/soffice")
        if candidate.is_file():
            return str(candidate)
    return None


def validate_pages(source):
    try:
        with zipfile.ZipFile(source) as archive:
            members = archive.infolist()
            total = sum(item.file_size for item in members)
            if not members or len(members) > 10000 or total > 2 * 1024**3:
                raise ConversionError("archive_limit")
            for item in members:
                if (
                    item.flag_bits & 1
                    or item.file_size > 512 * 1024**2
                    or item.file_size > max(item.compress_size, 1) * 500
                ):
                    raise ConversionError("archive_limit")
            names = {item.filename for item in members}
            if not (
                any(name.startswith("Index/") for name in names)
                or "index.xml" in names
                or "index.xml.gz" in names
                or "Index.zip" in names
            ):
                raise ConversionError("invalid_pages")
    except (zipfile.BadZipFile, OSError) as exc:
        raise ConversionError("invalid_pages") from exc


def _stop(process):
    if process.poll() is None:
        if platform.system() == "Windows":
            subprocess.run(
                ["taskkill", "/PID", str(process.pid), "/T", "/F"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                creationflags=subprocess.CREATE_NO_WINDOW,
                timeout=15,
                check=False,
            )
        else:
            import signal

            try:
                os.killpg(process.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
        if process.poll() is None:
            process.kill()
    process.wait(timeout=15)


def convert_pages(source, destination, cancel):
    validate_pages(source)
    soffice = find_soffice()
    if not soffice:
        raise ConversionError("converter_missing")
    with tempfile.TemporaryDirectory(prefix="pages-lo-") as workspace:
        profile = Path(workspace) / "profile"
        (profile / "user").mkdir(parents=True)
        # Highest macro security; no trusted locations in this fresh profile.
        (profile / "user/registrymodifications.xcu").write_text(
            '<?xml version="1.0" encoding="UTF-8"?>'
            '<oor:items xmlns:oor="http://openoffice.org/2001/registry">'
            '<item oor:path="/org.openoffice.Office.Common/Security/Scripting">'
            '<prop oor:name="MacroSecurityLevel" oor:op="fuse"><value>3</value></prop>'
            "</item></oor:items>",
            encoding="utf-8",
        )
        output = Path(workspace) / "output"
        output.mkdir()
        kwargs = (
            {"creationflags": subprocess.CREATE_NO_WINDOW} if os.name == "nt" else {"start_new_session": True}
        )
        # Discard engine output: it may contain absolute paths or document content.
        with subprocess.Popen(
            [
                soffice,
                f"-env:UserInstallation={profile.as_uri()}",
                "--headless",
                "--norestore",
                "--nodefault",
                "--convert-to",
                "docx:Office Open XML Text",
                "--outdir",
                str(output),
                str(source),
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            **kwargs,
        ) as process:
            deadline = time.monotonic() + 300
            try:
                while process.poll() is None:
                    if cancel.wait(0.15):
                        raise Cancelled()
                    if time.monotonic() >= deadline:
                        raise ConversionError("conversion_timeout")
            finally:
                _stop(process)
            generated = output / (source.stem + ".docx")
            if cancel.is_set():
                raise Cancelled()
            if process.returncode != 0 or not generated.is_file():
                raise ConversionError("unsupported_document")
            try:
                with zipfile.ZipFile(generated) as archive:
                    if "word/document.xml" not in archive.namelist():
                        raise ConversionError("invalid_output")
            except zipfile.BadZipFile as exc:
                raise ConversionError("invalid_output") from exc
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(generated), destination)
