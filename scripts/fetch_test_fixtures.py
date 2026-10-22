"""Download pinned, public engine regression fixtures to an ignored directory."""

import hashlib
import urllib.request
from pathlib import Path

COMMIT = "6d19ce365f64a6217791a9438c85f4b1851ca7e0"
FIXTURES = {
    "pages4-file.pages": "793d9ece44e30c646a6b0c1d19e1feb314f94c2850e5da6d159326cd17991b4f",
    "pages5-file.pages": "b5de90dfa78077c62e1c88ddaa188e412ffa9dd31558e2774715733f9d58dfe7",
}


def main():
    destination = Path(__file__).resolve().parents[1] / "test-results/fixtures"
    destination.mkdir(parents=True, exist_ok=True)
    for name, expected in FIXTURES.items():
        url = f"https://raw.githubusercontent.com/LibreOffice/libetonyek/{COMMIT}/src/test/data/{name}"
        with urllib.request.urlopen(url, timeout=30) as response:
            contents = response.read(1024 * 1024)
        if hashlib.sha256(contents).hexdigest() != expected:
            raise SystemExit(f"Fixture checksum mismatch: {name}")
        (destination / name).write_bytes(contents)
        print(f"Verified {name}")


if __name__ == "__main__":
    main()
