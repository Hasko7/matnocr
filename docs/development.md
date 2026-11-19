# Development and Contributing

[Back to the README](../README.md)

Before making substantial changes, read [AGENTS.md](../AGENTS.md),
[PROJECT.md](../PROJECT.md), and [TODO.md](../TODO.md). Keep changes small and easy
to review, cover Arabic/RTL examples, and measure performance before and after
pipeline changes. Do not add private book pages as public test data; prefer
synthetic or public-domain documents.

## Editable CLI Installation

For a `matnocr` command that follows source edits in this checkout:

```powershell
uv tool install --editable .
```

An editable installation picks up source changes directly. A regular
`uv tool install .` installation has its own copy and can be refreshed with
`uv tool install --reinstall .`. For project development, `uv run matnocr`
uses the project environment directly; `uv run python -m matnocr` also works.

## Local Checks

The development dependency group already includes Ruff, ty, pytest, and
pytest-cov. Local commands:

```powershell
uv sync --locked
uv run pytest
uv run pytest -m "not integration"
uv run pytest -m integration
uv run pytest --cov=matnocr
uv run ruff check .
uv run ruff format --check .
uv run ty check
```

To apply formatting, run `uv run ruff format .`.
Ruff, ty, pytest, and branch coverage are configured in `pyproject.toml`.
Ruff targets Python 3.11 and checks common syntax errors, undefined names,
imports, modernization, and common bug patterns. Its formatter uses 88 columns
and double quotes. The historical `prototype.py` and `add_new_white_page.py`
experiments are excluded from Ruff; ty checks `src/` and `tests/`, targeting
Python 3.11 on Windows. These scripts are not distributed application code.

The installed PyWinRT typing works with ty without global rule suppression or
missing-import exceptions. `Any` remains at the existing native OCR/bitmap
boundaries and in test doubles, where dynamic projection objects are passed
through. Core configuration, page selection, and output functions remain typed.

Integration tests are marked `integration` and live in `tests/integration/`.
They generate original English, German, and Arabic PDFs at runtime and check
PDFium rendering, SoftwareBitmap copying, and real OCR. The German and Arabic
documents contain only scan images, generated with Windows text shaping to
preserve umlauts, eszett, and connected Arabic letters. Tests check selected
words and their order rather than requiring identical punctuation.

Windows tests skip when Windows or the required WinRT module is unavailable;
each language-specific OCR test skips if its language pack is missing.
Generating the Unicode scans also requires Windows PowerShell, System.Drawing,
and the locally installed Arial font; affected tests skip if these capabilities
are unavailable. No new package dependencies or bundled font files are needed.
No language packs are installed by tests, and no private book pages are used.
See [the integration test notes](../tests/integration/README.md) for details.
The full suite currently requires Windows
because application modules imported by unit tests use WinRT. GitHub CI remains
a later roadmap task.

