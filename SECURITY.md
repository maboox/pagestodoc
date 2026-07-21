# Security Policy

## Reporting a vulnerability

Please do not disclose security vulnerabilities in a public issue. Use GitHub's **Report a vulnerability** feature in the repository Security tab.

Include the affected version, reproduction steps, expected impact, and any suggested mitigation.

## Security model

Pages Converter is designed for local use:

- The server binds to `127.0.0.1` only.
- No files are uploaded to third-party services.
- Relative paths are sanitized before writing.
- Conversion runs through the locally installed LibreOffice executable.
- Temporary job data is scheduled for deletion.

Changing the bind address, exposing the server through a proxy, or running modified code can change this security model.

## Supported versions

Security fixes are provided for the latest release.
