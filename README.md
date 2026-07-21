# Pages Converter

A private, local-first batch converter for Apple Pages documents on Windows.

Select an entire folder, convert every `.pages` file to `.docx`, preserve the original directory structure, and copy all non-Pages files unchanged into one downloadable ZIP archive.

![Pages Converter interface](docs/screenshot.png)

## Highlights

- **Batch conversion** — processes multiple `.pages` files in one run.
- **Folder-aware** — scans nested folders and preserves their structure.
- **Pass-through files** — PDF, DOCX, images, archives, and other files are copied unchanged.
- **Live progress** — shows percentage, current file, converted files, copied files, and errors.
- **Local-first** — binds only to `127.0.0.1`; files never leave your computer.
- **No Python packages** — the server uses only the Python standard library.
- **Failure-safe** — if conversion fails, the original `.pages` file remains in the output and the error is recorded.
- **Persian interface** — responsive UI with light and dark mode support.

## Requirements

| Requirement | Version / notes |
| --- | --- |
| Windows | Windows 10 or 11 recommended |
| Python | Python 3.10 or newer |
| LibreOffice | Latest stable release recommended |
| Browser | Chrome or Edge recommended for folder selection |

> Apple Pages is not available on Windows. Conversion is performed locally by LibreOffice, so complex layouts may not be reproduced perfectly.

## Quick start

1. Install [Python](https://www.python.org/downloads/windows/).
   - Enable **Add Python to PATH** during installation.
2. Install [LibreOffice](https://www.libreoffice.org/download/download-libreoffice/).
3. Download or clone this repository:

   ```bash
   git clone https://github.com/maboox/pagestodoc.git
   cd pages-converter
   ```

4. Double-click `start.bat`.
5. Your browser opens at `http://127.0.0.1:8765`.
6. Choose a folder and click **Process and download ZIP**.

### Manual start

```bash
python app.py
```

To use another port:

```bat
set PORT=9000
python app.py
```

## How it works

Given this folder:

```text
Project/
├── Client A/
│   ├── Contract.pages
│   └── Reference.pdf
└── Client B/
    └── Reports/
        └── July.pages
```

Pages Converter produces:

```text
Project/
├── Client A/
│   ├── Contract.docx
│   └── Reference.pdf
└── Client B/
    └── Reports/
        └── July.docx
```

| Input | Output behavior |
| --- | --- |
| `.pages` | Converted to `.docx` |
| Any other file | Copied unchanged |
| Failed `.pages` conversion | Original file retained; details added to `conversion-errors.txt` |
| Empty folder | Not included because browsers do not upload empty directories |

## Privacy and security

- The HTTP server listens only on `127.0.0.1`, not on your network interface.
- No analytics, telemetry, accounts, cookies, or cloud APIs are used.
- Uploaded files are written to a temporary local directory.
- Temporary jobs are removed automatically after completion or failure.
- Relative paths are sanitized before files are written, preventing directory traversal.

Do not modify the host binding to `0.0.0.0` unless you understand the security implications.

## Troubleshooting

### `Python was not found`

Reinstall Python and enable **Add Python to PATH**, or add these folders to your user `PATH`:

```text
C:\Users\YOUR_NAME\AppData\Local\Programs\Python\Python3xx\
C:\Users\YOUR_NAME\AppData\Local\Programs\Python\Python3xx\Scripts\
```

### `LibreOffice was not found`

Install LibreOffice in its default location, or add this directory to `PATH`:

```text
C:\Program Files\LibreOffice\program
```

### A Pages file was not converted

- Update LibreOffice to the latest stable version.
- Open the file in LibreOffice manually to verify compatibility.
- Check `conversion-errors.txt` in the downloaded ZIP.
- For pixel-perfect results, export from Apple Pages on macOS or iCloud instead.

### The progress appears paused

Large Pages documents can take several minutes in LibreOffice. The current filename remains visible while conversion is active.

## Project structure

```text
pages-converter/
├── app.py                 # Local HTTP server, jobs, conversion, and ZIP creation
├── index.html             # Self-contained web interface
├── start.bat              # Windows launcher and dependency checks
├── docs/
│   ├── screenshot.png
│   └── README.fa.md       # Persian documentation
├── CONTRIBUTING.md
├── SECURITY.md
├── CHANGELOG.md
├── LICENSE
└── README.md
```

## Development

No dependency installation is required.

```bash
python -m py_compile app.py
python app.py
```

Health check:

```text
http://127.0.0.1:8765/health
```

Before opening a pull request, verify folder preservation, pass-through files, conversion errors, progress reporting, and ZIP download behavior.

## Limitations

- LibreOffice does not support every Pages feature.
- Fonts unavailable on Windows may be substituted.
- Complex typography, media, charts, and page geometry may change.
- The request size limit is 1 GB per batch.
- Empty directories cannot be preserved through browser folder uploads.

## Contributing

Issues and pull requests are welcome. Please read [CONTRIBUTING.md](CONTRIBUTING.md) before contributing. Security concerns should follow [SECURITY.md](SECURITY.md).

## License

Released under the [MIT License](LICENSE).
