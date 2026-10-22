"""Portable paths and deterministic, case-insensitive collision handling."""

import re
import unicodedata
from pathlib import PurePosixPath

RESERVED = re.compile(r"^(CON|PRN|AUX|NUL|CONIN\$|CONOUT\$|CLOCK\$|COM[1-9¹²³]|LPT[1-9¹²³]) *(?:\.|$)", re.I)


def validate_path(raw):
    if not isinstance(raw, str) or not raw or len(raw) > 220:
        raise ValueError("invalid_path")
    raw = unicodedata.normalize("NFC", raw.replace("\\", "/"))
    parts = raw.split("/")
    for part in parts:
        if (
            not part
            or part in (".", "..")
            or len(part) > 120
            or part.endswith((".", " "))
            or RESERVED.match(part)
            or any(
                ord(c) < 32 or c in '<>:"|?*' or unicodedata.category(c) in ("Cc", "Cs", "Co") for c in part
            )
            or any(c in "\u202a\u202b\u202c\u202d\u202e\u2066\u2067\u2068\u2069" for c in part)
        ):
            raise ValueError("invalid_path")
    return PurePosixPath(*parts)


class PathAllocator:
    """Reserve files and directories together; never overwrite an input."""

    def __init__(self):
        self.nodes = {}

    def reserve(self, path):
        parent = PurePosixPath()
        for index, part in enumerate(path.parts):
            directory = index < len(path.parts) - 1
            candidate = parent / part
            counter = 2
            while candidate.as_posix().casefold() in self.nodes:
                existing, is_directory = self.nodes[candidate.as_posix().casefold()]
                if directory and is_directory:
                    candidate = existing
                    break
                name = PurePosixPath(part)
                candidate = parent / (
                    f"{part}-{counter}" if directory else f"{name.stem}-{counter}{name.suffix}"
                )
                counter += 1
            self.nodes[candidate.as_posix().casefold()] = (candidate, directory)
            parent = candidate
        return parent
