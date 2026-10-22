# Third-party notices

Application code is MIT licensed. Runtime Python packages are installed separately using `requirements.txt`; they are not vendored into this repository. LibreOffice is also installed separately and remains governed by its own licenses.

| Component | Version / source | License / included notice |
| --- | --- | --- |
| Werkzeug | 3.1.9, Pallets | BSD-3-Clause, installed package metadata |
| Waitress | 3.0.2, Pylons Project | ZPL-2.1, installed package metadata |
| MarkupSafe | 3.0.4, Pallets | BSD-3-Clause, installed package metadata |
| Lucide static SVG subset | 1.61.0, `lucide-static` | [ISC and inherited icon notices](assets/Lucide-LICENSE.txt) |
| Inter variable font | 4.1, rsms/inter | [SIL Open Font License 1.1](assets/fonts/Inter-LICENSE.txt) |
| Vazirmatn variable font | 33.003, rastikerdar/vazirmatn | [SIL Open Font License 1.1](assets/fonts/Vazirmatn-OFL.txt) |

Icon geometry is stored in `assets/icons.svg`; the code/repository glyph is an equivalent simple code icon, not a GitHub brand logo. The app uses no CDN at runtime. Local font files are unchanged upstream assets. Screenshots show synthetic example filenames, without user documents.

Optional integration tests download two upstream libetonyek regression fixtures to an ignored test directory, with a fixed source commit and SHA-256 validation. Those third-party fixture binaries are not distributed in this repository or source release. See their upstream project for applicable licensing. Development-only tooling and transitive licenses are described by `package-lock.json` and their installed package notices.
