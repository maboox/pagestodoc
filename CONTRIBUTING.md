# Contributing to Pages Converter

Thank you for helping improve Pages Converter.

## Before you start

- Search existing issues before opening a new one.
- Keep changes focused and avoid unrelated refactors.
- Never add telemetry, cloud uploads, or external runtime dependencies without prior discussion.
- Preserve the local-only security model and directory traversal protections.

## Development setup

Pages Converter uses the Python standard library and a self-contained HTML interface.

```bash
python -m py_compile app.py
python app.py
```

LibreOffice is required for real `.pages` conversion tests.

## Pull requests

1. Create a focused branch.
2. Explain the user-facing problem and your solution.
3. Test nested folders, pass-through files, failed conversions, progress updates, and ZIP contents.
4. Test the interface at desktop and mobile widths.
5. Update the README and CHANGELOG when behavior changes.

## Style

- Prefer clear, dependency-free Python.
- Keep the server bound to `127.0.0.1`.
- Sanitize every user-provided path.
- Keep the UI accessible and keyboard-friendly.
- Do not silently discard input files.
