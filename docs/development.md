# Development and Contributing

[Back to the README](../README.md)

For issue reporting, pull requests, and contribution expectations, start with
[CONTRIBUTING.md](../CONTRIBUTING.md) and the
[Code of Conduct](../CODE_OF_CONDUCT.md). Follow [SECURITY.md](../SECURITY.md)
for vulnerability reports.

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
experiments are excluded from Ruff; ty checks `src/`, `tests/`, and `tools/`, targeting
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
The full suite currently requires Windows because application modules imported
by unit tests use WinRT.

## GitHub Actions CI

The workflow in [ci.yml](../.github/workflows/ci.yml) runs on pushes to `main`,
pull requests targeting `main`, and manual dispatch. Each matrix job uses
`windows-2025` with Python 3.11, 3.12, 3.13, or 3.14. setup-uv selects the matrix
interpreter independently of the local `.python-version` file. uv is pinned to
0.12.19, and third-party actions are pinned to commit SHAs. The workflow has
read-only repository permissions and does not publish artifacts or use deployment
secrets.

Every Windows job synchronizes `uv.lock`, logs the runtime and available OCR
languages, runs Ruff, formatting, ty, and all tests with coverage, and builds a
wheel and source distribution. It then creates a separate environment, installs
the locked runtime dependencies and built wheel, and runs `tools/ci_smoke.py`
with isolated Python imports. The smoke test verifies that the imported package
lives in that environment, checks CLI help/version output, and invokes the
installed `matnocr.exe` console entry point. It deliberately uses OCR-command
help rather than requiring an OCR engine for help on a server runner.

OCR capabilities on Windows Server runners may differ from a desktop Windows
installation. Integration tests skip an unavailable OCR runtime or missing
language pack and report the reasons. The diagnostics step records the actual
languages without installing system capabilities or opening an administrative
PowerShell. CLI unit tests use synthetic language discovery.

The final `CI` job runs even if a matrix job fails or is skipped, and succeeds
only when the Windows matrix succeeds. It is required by the active `main`
ruleset, which also requires branches to be up to date. The verified hosted
matrix passes on Python 3.11–3.14 with 142 tests passing per version; German and
Arabic OCR tests skip because the runner only provides `en-US`. Locally, all
144 tests pass on Python 3.13 with those language packs installed. Inspect skips
when evaluating future compatibility. The final gate uses Ubuntu only to combine
results; all application checks run on Windows.

