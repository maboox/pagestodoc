# Testing

## Python regression tests

Activate the project's `.venv`, install `requirements.txt` and `requirements-dev.txt`, then run:

```sh
python -m unittest discover -s tests -v
python -m ruff check .
python -m ruff format --check .
python -m pip_audit -r requirements.txt
```

The standard suite requires no document-engine installation. It exercises portable paths, Unicode, case/file/directory collisions, pass-through byte preservation, existing DOCX priority, failure originals, report collisions, limits, cancellation, deletion, retention, active readers, session authorization, CSRF, foreign Host/Origin, malformed uploads, and HTTP ZIP round trips. Unit conversion fakes isolate application behavior from engine compatibility.

## Real LibreOffice integration

Install a supported LibreOffice release and download the two public, pinned upstream fixtures:

```sh
python scripts/fetch_test_fixtures.py
# PowerShell:
$env:PAGES_TEST_FIXTURES = (Resolve-Path test-results/fixtures).Path
# POSIX shells:
export PAGES_TEST_FIXTURES="$PWD/test-results/fixtures"
python -m unittest discover -s tests -v
```

The fetch script pins a libetonyek source commit, validates SHA-256, and stores third-party files only under ignored `test-results/`. The integration test converts Pages 4 and Pages 5 fixtures with the real engine and validates the generated Word package. Fixtures are not part of release archives. Tests skip explicitly when `PAGES_TEST_FIXTURES` is unset; the CI integration job sets it and requires the engine.

These regression fixtures demonstrate format handling; they do not establish fidelity for all real documents. Fonts, tables, embedded media, pagination, and complex layouts need human review with representative non-confidential documents.

## Browser and accessibility

```sh
npm ci
npx playwright install chromium
npm run check
npm run test:ui
```

The UI test starts its own app server, tests Persian and English, both themes, selection, a real browser ZIP download, reload recovery, output deletion, responsive widths, and lack of outbound app requests. It also exercises the direct-save fetch/stream path with a controlled writable destination; the native OS save dialog still needs manual verification. Axe checks WCAG A/AA rules. Screenshots and reports go to ignored `test-results/`. Automated checks do not replace a complete manual accessibility audit.

To use an installed browser, set `PAGES_BROWSER_CHANNEL=chrome` or `msedge`. If Python is not in `.venv`, set `PYTHON` to its executable. Set `PAGES_SCREENSHOTS=1` only when intentionally refreshing the synthetic screenshots in `docs/`. Avoid capturing user filenames or developer paths.

Some installed/managed headless browsers block `.zip` attachments even from an independent loopback server. For diagnosis only, `PAGES_SKIP_NATIVE_DOWNLOAD=1` explicitly skips that single attachment assertion while retaining the direct-save stream and API checks. CI uses the bundled Chromium and does not enable this skip. Do not describe a skipped check as a verified native download.

## Offline installation

On a connected machine with a compatible Python version and operating system:

```sh
python -m pip download -r requirements.txt -d wheels
```

Transfer the source and wheels to the target computer, create `.venv`, and install using its Python:

```sh
python -m pip install --no-index --find-links wheels -r requirements.txt
```

Run `app.py` with that environment's Python. Obtain and install LibreOffice separately from its official distribution. Fonts and icons are already local. Do not commit wheel downloads, real documents, or test outputs.
