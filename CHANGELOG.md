# Changelog

## 2.0.0 — 2026-10-22

### Added

- Yellow document workspace with Persian/English, RTL/LTR, light/dark themes, local fonts and Lucide icons.
- Recursive directory drops in Chromium, file removal, batch summary, staged progress, cancellation, manual/repeat ZIP downloads, and session reload recovery.
- Per-file input/output JSON reports, collision-safe naming, download expiry and explicit output deletion.
- Modular conversion, job, path, and WSGI layers; pinned runtime dependencies; first-run environment setup and cross-platform launchers.
- Regression, HTTP security, native conversion, browser and automated accessibility checks; bilingual documentation and release guidance.

### Fixed

- Unauthenticated cross-origin access to the loopback API and DNS rebinding exposure.
- Memory-heavy multipart parsing and whole-archive downloads.
- Windows device names, case-only duplicates, input file/directory collisions, and existing DOCX files colliding with converted output.
- Mutable file selection during processing, flattened dropped folders, hard-coded launcher port, and missing conversion-engine feedback.
- Internal diagnostic/path disclosure, missing native conversion limits, and cleanup on cancelled/failed work.
- Removed the broken AppleScript fallback that referenced a missing script.

### Changed

- Requires the pinned Python packages and a separately installed LibreOffice. First-time setup needs PyPI access; app resources remain local.
- Batch limits: 1 GiB, 500 files, one active job, three retained results. Unsafe portable paths are rejected instead of silently sanitized.
- `pages-converter-report.json` replaces the ambiguous plain-text error report. Original inputs and existing Word files take priority over generated names.
- Git commit identities use a public noreply email. Existing public history is retained with personal email metadata removed.

## 1.x

Initial local Pages converter with folder-aware conversion, pass-through files, progress polling, and a Persian interface.
