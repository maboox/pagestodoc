# Contributing

Focused bug reports, accessibility fixes, translations, and conversion regressions are welcome. Use synthetic documents in issues and PRs. Report vulnerabilities privately using [SECURITY.md](SECURITY.md).

## Setup

```sh
python -m venv .venv
# Activate .venv using your shell, then:
python -m pip install -r requirements.txt -r requirements-dev.txt
npm ci
npx playwright install chromium
python app.py
```

LibreOffice is needed for actual Pages conversion; HTTP and file-pipeline unit tests use controlled fakes. See [testing](docs/TESTING.md) for real fixtures and browser checks.

## Before opening a PR

1. Reproduce the user-facing problem and add a meaningful regression test where behavior changes.
2. Run `python -m unittest discover -s tests -v`, `python -m ruff check .`, `python -m ruff format --check .`, `npm run check`, and `npm run test:ui`.
3. Exercise FA/RTL and EN/LTR, keyboard operation, light/dark themes, and mobile widths when touching the interface.
4. Preserve byte-identical pass-through content, failure originals, folder structure, cancellation, and collision safety.
5. Update user docs and the changelog when behavior changes. Keep dependency pins, notices, and lockfiles current.

## Design and security boundaries

Keep the yellow accent, readable contrast, local assets, reduced-motion support, and clear progress/error states. Use DOM text APIs for user-controlled filenames. Avoid adding a framework or dependency without a concrete benefit. Keep parsing, job lifecycle, conversion, and HTTP routing separate. Never expose engine diagnostics or personal paths to the browser. Do not widen the network binding, add cloud uploads, or add analytics as a routine refactor.

Use a public alias and GitHub noreply email for commits. Do not commit test outputs, screenshots of personal files, credentials, or private environment files. English code comments and technical docs are preferred; user-facing strings belong in both translation dictionaries.
