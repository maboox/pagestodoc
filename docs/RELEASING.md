# Release checklist

1. Update `pages_converter.__version__`, the UI footer, `package.json`/lock, and changelog together.
2. Review dependency updates and third-party notices; update all exact runtime pins together.
3. Pass Python tests on supported CI platforms, real-engine integration, lint/format, browser flows, and accessibility checks.
4. Run `pip-audit -r requirements.txt`, `npm audit`, and a redacted secret scan on both files and full Git history.
5. Review screenshots, commit identities, README links, and archive contents for private data. Keep synthetic filenames in screenshots.
6. Wait for CI on the exact release commit, then tag `vX.Y.Z`. Build the source archive from the tagged Git tree with `git archive`, not the developer working directory. Publish a SHA-256 checksum beside it.
7. Create a GitHub Release with English and Persian notes, setup requirements, and the source archive/checksum. State that Python and LibreOffice are required; do not call a source ZIP a standalone installer.
8. Keep `main` protected after publication, with passing checks and no force pushes. Enable secret scanning, push protection, dependency alerts, and private vulnerability reporting.

History cleanup needs separate care: make a private local backup, inspect exactly which refs and metadata change, preserve source trees, and use an explicit `--force-with-lease` expectation. Never rewrite unrelated repositories or delete unmerged branches merely because their names look old. A rewritten branch cannot remove old objects from other clones or GitHub caches; follow GitHub's removal process if sensitive data was published.
