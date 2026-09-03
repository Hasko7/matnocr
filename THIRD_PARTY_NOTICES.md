# Third-Party Notices – MatnOCR

MatnOCR is licensed under the Apache License 2.0. Third-party components remain under their own licenses.

## Runtime dependencies

### pypdfium2 / PDFium

- pypdfium2: Apache-2.0 / BSD-3-Clause
- PDFium: BSD-style license
- PDFium binary distributions include additional third-party components under their respective licenses.

When distributing MatnOCR as a bundled Windows executable or archive, include the PDFium license and the third-party license notices shipped with the pypdfium2 wheel/build. Do not replace those notices with this summary.

### PyWinRT

PyWinRT and the modular `winrt-*` projection packages are licensed under the MIT License.

### Typer

Typer is licensed under the MIT License. Its transitive dependencies retain their own licenses.

### Rich

Rich is licensed under the MIT License. Its transitive dependencies retain their own licenses.

## Development dependencies

- Ruff: MIT
- ty: MIT
- pytest: MIT

## Packaging rule

Before every binary release, regenerate or verify the complete third-party license bundle from the exact locked dependency versions used for that release.
