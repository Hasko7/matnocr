# TODO – MatnOCR

> Project name, package name, and CLI command: `MatnOCR` / `matnocr`.

## Phase 0 – Decisions before project setup

### 1. Choose a project name

- [x] Collect name ideas
- [x] Prefer short, memorable names
- [x] Check whether the name works well as a CLI command
- [x] Check PyPI for name conflicts
- [x] Check GitHub for name conflicts
- [x] Check winget for name conflicts
- [x] Check npm for name conflicts
- [x] Check Cargo for name conflicts
- [x] Check search engines for name conflicts
- [x] Choose the final package name: `matnocr`
- [x] Choose the final CLI command: `matnocr`
- [x] Choose the final GitHub repository name: `matnocr`

Decision:

```text
Brand:       MatnOCR
PyPI:        matnocr
CLI:         matnocr
Python pkg:  matnocr
GitHub repo: matnocr
Executable:  matnocr.exe
```

### 2. Compare PDF renderers: PyMuPDF vs. pypdfium2

- [x] Create a `pypdfium2` test project
- [x] Render PDF pages directly in RAM
- [x] Convert the PDFium buffer directly to `SoftwareBitmap`
- [x] Use the same six benchmark pages
- [x] Test at 200 DPI
- [x] Test at 250 DPI
- [x] Test at 300 DPI
- [x] Compare rendering time
- [x] Compare bitmap conversion time
- [x] Compare OCR time
- [x] Compare total time
- [ ] Compare memory usage *(not blocking for v0.1)*
- [x] Compare OCR output
- [ ] Compare installation and wheel size *(wheel size still to be measured; not blocking)*
- [x] Document licensing implications
- [x] Choose the final renderer: `pypdfium2`

Decision:

```text
pypdfium2 + permissive project license
```

Rationale:

- Direct original-scan fast path for scanned PDFs
- OCR quality at 200 / 250 / 300 DPI is practically on par with PyMuPDF
- No temporary PNG files or Pillow required
- Preserves the Direct-RAM pipeline
- Keeps normal PDFium page rendering as a fallback
- More permissive licensing than PyMuPDF/AGPL

### 3. Choose a license

- [x] Wait for the renderer decision
- [x] Check core dependencies and their licenses
- [x] Choose between AGPL / MIT / Apache-2.0
- [x] Choose the project license: `Apache-2.0`
- [x] Create `LICENSE`
- [x] Document third-party licensing obligations (`THIRD_PARTY_NOTICES.md`)
- [x] Add the license to `pyproject.toml`
- [x] Add license information to the README
- [ ] Include complete PDFium and third-party license files in Windows binary releases

License decision:

```text
MatnOCR: Apache-2.0
```

Key dependencies:

```text
pypdfium2 / PDFium    permissive (Apache-2.0 / BSD-3-Clause or BSD-style + third-party licenses)
PyWinRT                MIT
Typer                  MIT
Rich                   MIT
Ruff                   MIT
ty                     MIT
pytest                 MIT
```

Configured in `pyproject.toml`:

```toml
[project]
license = "Apache-2.0"
license-files = ["LICENSE", "THIRD_PARTY_NOTICES.md"]
```

## Phase 1 – Set up the project

### 4. Create a new Git project

- [x] Use the existing project directory with the final name
- [x] `git init`
- [x] Create `.gitignore` for Python / uv / VS Code / build artifacts
- [x] Choose the initial branch strategy (`main`)
- [x] Create the first commit

### 5. Initialize the uv project

- [x] `uv init --app`
- [x] Set the minimum Python version, initially `>=3.11`
- [x] Use a `src/` layout
- [x] Generate `uv.lock`
- [x] Evaluate and configure `uv_build` as the build backend
- [x] Add runtime dependencies
- [x] Add development dependencies

### 6. Create the planned package structure

- [x] `src/matnocr/__init__.py`
- [x] `src/matnocr/__main__.py`
- [x] `src/matnocr/cli.py`
- [x] `src/matnocr/engine.py`
- [x] `src/matnocr/renderer.py`
- [x] `src/matnocr/languages.py`
- [x] `src/matnocr/pages.py`
- [x] `src/matnocr/rtl.py`
- [x] `src/matnocr/output.py`
- [x] `src/matnocr/config.py`
- [x] `src/matnocr/ui.py`

### 7. Modularize the current OCR prototype

- [x] Extract Windows OCR code from the test script
- [x] Move engine creation to its own module
- [x] Preserve the Direct-RAM pipeline
- [x] Abstract the PDF renderer
- [x] Move RTL reconstruction to its own module
- [x] Separate language resolution
- [x] Separate output generation
- [x] Make timing code optional and structured
- [x] Remove global project variables
- [x] Validate suspicious non-text pages with a controlled 125 DPI OCR pass and discard OCR artifacts

## Phase 2 – Build the v0.1 CLI

### 8. Integrate Typer + Rich

- [x] Add Typer
- [x] Add Rich
- [x] Create the main app
- [x] Design a helpful `--help` display
- [x] Define the color and panel design
- [x] Define consistent error messages
- [x] Support terminals without ANSI and CI environments

### 9. Configure the console entry point

- [x] Configure `[project.scripts]`
- [x] `matnocr = "matnocr.cli:app"`
- [x] Test local installation
- [x] Verify that `matnocr --help` works
- [x] Support `python -m matnocr` as well

### 10. Implement basic arguments

- [x] PDF as a positional argument
- [x] `--lang`
- [x] `--dpi`
- [x] `--quality`
- [x] `-o / --output`
- [x] `--quiet`
- [x] `--version`

### 11. Implement DPI presets

- [x] `fast -> 200`
- [x] `balanced -> 250`
- [x] `quality -> 300`
- [x] Handle conflicts between `--quality` and `--dpi` clearly
- [x] Set the default mode: `quality` / 300 DPI

### 12. Implement page-range parsing

Support:

```text
30-50
1,5,20-35,100
```

- [x] Individual pages
- [x] Ranges
- [x] Combinations
- [x] Remove duplicates
- [x] Define ordering: ascending by PDF page number
- [x] Reject invalid page numbers
- [x] Reject pages outside the PDF
- [x] Write helpful error messages
- [x] Show PDF page count with `--page-count`

### 13. `languages` command

- [x] Discover installed Windows OCR languages dynamically
- [x] Display language codes
- [x] Display readable language names
- [x] Show active and available languages in a Rich table
- [x] Explain missing languages during OCR clearly
- [x] Save a persistent default language with `languages default <code>`
- [x] Manage language packs through administrative Windows PowerShell
- [x] Install languages with `languages install <code>` and remove them with `languages remove <code>`
- [x] List all available Windows OCR capabilities dynamically with `languages available`
- [x] Open administrative PowerShell through Windows UAC when MatnOCR is not elevated
- [x] Show the selected default language in `matnocr languages`
- [x] Show the default language in the main `matnocr` help text

### 14. `doctor` command

Check:

- [x] Supported Windows version
- [x] Availability of Windows.Media.Ocr
- [x] Installed OCR languages
- [x] Availability of the PDF renderer
- [x] Working Direct-RAM conversion
- [x] Maximum OCR image dimension
- [x] Display Python version
- [x] Display package version
- [x] Show diagnostic results clearly with ✓ / ✗

### 15. Progress UI

- [x] Rich progress bar
- [x] Current page
- [x] Page count
- [x] Speed in pages per second
- [x] Elapsed time
- [x] ETA
- [x] Show a summary after completion
- [x] Support `--quiet` without animation

Example target:

```text
OCR  ████████████████████████████████  71/71

71 pages · 23.4s · 3.03 pages/s

✓ Saved to output.txt
```

### 16. Output v0.1

- [x] Keep TXT as the initial default
- [x] Bring simple Markdown with `# Page <PDF page number>` forward from v0.2
- [x] Save the default output format with `output default txt|md` and show it with `output`
- [x] Show available output formats and examples in `output` and `output --help`
- [x] Support one-time format selection with `--format txt|md`
- [x] Select the format from the `-o` extension (`.txt`, `.md`, `.markdown`)
- [x] Append the selected format extension to extensionless targets; reject invalid or conflicting extensions before OCR
- [x] Preserve format and language settings when saving either preference
- [x] Preserve page markers
- [x] Write UTF-8
- [x] Generate automatic filenames
- [x] Preserve OCR line breaks from `OcrLine` by default
- [x] Detect paragraphs from bounding boxes in the default layout mode
- [x] Disable layout with `--no-layout` and join text continuously
- [x] Preserve layout without a second OCR pass or temporary raster files
- [x] Avoid accidental overwrites of existing files
- [x] Define `--output` and format-selection behavior, with `--force` for deliberate overwrites
- [x] Handle unwritable output paths cleanly

## Phase 3 – Quality and tests

### 17. Configure Ruff

- [x] Add Ruff as a development dependency
- [x] `ruff check`
- [x] `ruff format`
- [x] Configure appropriate rules in `pyproject.toml`
- [x] Document local formatting (`README.md`)

### 18. Type Checking

- [x] Add `ty` as a development dependency
- [x] Run `ty` across the project
- [x] Configure `ty check`
- [x] Investigate PyWinRT typing issues
- [x] Document necessary exceptions

### 19. Configure pytest

- [x] Add pytest and pytest-cov as development dependencies
- [x] Create the unit-test structure
- [x] Create the integration-test structure
- [x] Configure pytest

### 20. Unit Tests

- [x] Page-Range-Parser
- [x] Language Resolution
- [x] RTL sorting
- [x] Filename generation
- [x] Quality-Presets
- [x] Output Formatting
- [x] CLI Validation
- [x] Configuration

### 21. Integration Tests

- [x] PDF-Renderer
- [x] Direct-RAM-Pipeline
- [x] SoftwareBitmap creation
- [x] Windows OCR
- [x] Real OCR on a small test document
- [x] Skip tests when the required OCR language is missing
- [x] Keep test data clear of copyright issues

### 22. Create original test PDFs

- [x] Synthetic English PDF (generated during the test)
- [x] Synthetic German scanned PDF with umlauts and ß (generated during the test)
- [x] Synthetic Arabic scanned PDF with connected letters and RTL checks (generated during the test)

The test texts are original. Public-domain texts remain an optional alternative,
not an additional required task.

Standing rule: Do not commit copyrighted book pages or private benchmark files.
System fonts are used only for local rendering; font files are not distributed.

## Phase 4 – Documentation and open source

### 23. Write the README

The README includes:

- [x] Project description
- [x] Screenshot / CLI example
- [x] Structure the README for new users and move detailed documentation to `docs/`
- [x] Prepare screenshot paths and instructions under `docs/images/`
- [x] Add a real terminal screenshot as `docs/images/terminal.png` (user)
- [x] Add an Arabic book page as `docs/images/book_page.png` with an unchanged OCR example (user)
- [x] Features
- [x] Installation
- [x] Add a short GitHub installation guide covering prerequisites, local cloning, and verified Python support
- [x] Quick Start
- [x] Languages
- [x] Windows OCR language packs
- [x] Page Ranges
- [x] DPI / Quality Modes
- [x] Benchmarks
- [x] Limitations
- [x] License
- [x] Contributing

### 24. Open-source files

- [x] `LICENSE`
- [x] `CONTRIBUTING.md`
- [x] `CHANGELOG.md`
- [x] `SECURITY.md`
- [x] `CODE_OF_CONDUCT.md`
- [x] `PROJECT.md`
- [x] `TODO.md`

### 25. GitHub Templates

- [x] Bug Report Template
- [x] Feature Request Template
- [x] Pull Request Template
- [x] OCR Quality Report Template

The OCR Quality Report asks for, among other things:

```text
language
Windows version
DPI
PDF type
page sample
expected text
actual OCR
```

## Phase 5 – GitHub Repository

### 26. Create the GitHub repository

- [x] Create a public repository
- [x] Set a description
- [x] Add topics
- [x] Display the license
- [x] Set `main` as the default branch
- [x] Set the local Git remote
- [x] Push the first commit
- [x] Check the issue forms on GitHub
- [x] Check the pull request template on the first real GitHub PR (PR #1)
- [x] Enable private vulnerability reporting and verify the reporting path in `SECURITY.md`
- [x] Define the moderation reporting path in `CODE_OF_CONDUCT.md`: GitHub reporting tools, intentionally without a public email address or direct private project contact

Possible topics:

```text
ocr
windows
pdf
arabic
cli
python
winrt
pdf-ocr
offline-ocr
```

### 27. Enable branch and release protection

- [x] Require pull requests before merging
- [x] Require successful CI (GitHub Actions `CI` check; branch must be up to date)
- [x] Prevent accidental force pushes
- [x] Protect tags and releases
- [x] Activate the `Protect version tags` ruleset for `v*`: block changes and deletion, with no bypass exceptions
- [x] Enable release immutability for future GitHub releases

New version tags can still be created. For releases, prepare a draft with all
assets before publishing. Published assets are then immutable; corrections
require a new version. Setup and procedure are documented in `docs/releases.md`.

## Phase 6 – GitHub CI

### 28. Create GitHub Actions CI

Workflow:

```text
push
pull_request
```

Steps:

- [x] Checkout
- [x] Install uv
- [x] Install Python
- [x] `uv sync --locked`
- [x] `ruff check`
- [x] `ruff format --check`
- [x] `ty check`
- [x] `pytest`
- [x] Build the package
- [x] Install the built wheel
- [x] CLI Smoke Test

The workflow is implemented and has passed on GitHub for Python 3.11–3.14.
The [successful run on main](https://github.com/Hasko7/matnocr/actions/runs/45465791622)
checks all four versions, including build, fresh wheel installation, and CLI
smoke tests. CLI tests create their own input paths; forced terminal formatting
is disabled in the workflow.

- [x] Verify the first successful GitHub run on the PR and on main (matrix and actual runner capabilities)

### 29. Windows Runner

- [x] Configure a Windows GitHub runner (`windows-2025`; hosted run successful)
- [x] Choose the runner image family (`windows-2025`; exact image version recorded in the Actions log)
- [x] Inspect available Windows OCR languages in the first GitHub run: `en-US`; German and Arabic are missing
- [x] Enable small integration tests in the workflow
- [x] Skip OCR language-dependent tests cleanly when the runtime or language is missing

### 30. Python CI Matrix

The Python 3.11–3.14 matrix passed on GitHub:

- [x] Python 3.11
- [x] Python 3.12
- [x] Python 3.13
- [x] Python 3.14

Each hosted job passes 142 tests; two OCR integration tests are skipped because
German and Arabic language packs are missing. Locally, all 144 tests pass on
Python 3.13 with those packs installed. The hosted matrix therefore does not
establish real German or Arabic OCR compatibility across all Python versions.

### 31. Security Automation

- [ ] Dependabot
- [ ] CodeQL
- [x] Set minimal GitHub Actions permissions (`contents: read` in the CI workflow)
- [x] Pin CI actions to verified commit SHAs and uv to a version

## Phase 7 – Python Packaging / PyPI

### 32. Finalize `pyproject.toml`

- [x] Package Metadata
- [x] Name
- [x] Version
- [x] Description
- [x] Readme
- [x] License
- [x] Authors
- [x] Python version
- [x] Dependencies
- [x] Optional Dev Dependencies
- [x] Project URLs
- [x] CLI Entry Point
- [x] Classifiers

Development tools remain in `[dependency-groups].dev` and are not part of the
published package dependencies. The wheel and sdist were built; their metadata,
CLI entry point, and included license files were checked.

### 33. Test the local build

- [x] `uv build`
- [x] Inspect the sdist
- [x] Inspect the wheel
- [x] Create a fresh virtual environment
- [x] Install the wheel there
- [x] Test the CLI thoroughly

The freshly built wheel was installed on Windows in a separate Python 3.13
environment with locked runtime dependencies. The repeatable
`tools/cli_full_smoke.py` test checks the installed console command and
`python -m matnocr`, help, version, diagnostics, languages, settings, page count,
real OCR on an original two-page PDF, TXT/Markdown, page selection, DPI,
`--quiet`, `--force`, and common error cases. Settings and test output stay in
a temporary directory. Installing or removing Windows language packs is outside
the scope of this local CLI test.

### 34. TestPyPI

- [x] Prepare a TestPyPI account and project
- [x] Upload the first test release
- [x] Test installation from TestPyPI

The user confirmed that version `0.1.0` was published to TestPyPI through the
workflow and installed successfully in a fresh environment; `matnocr --version`
and `matnocr doctor` passed.

### 35. PyPI Trusted Publishing

- [x] Create the PyPI project
- [x] Configure GitHub Trusted Publishing
- [x] Use OIDC instead of a long-lived API token
- [x] Create a separate release workflow

The separate `testpypi.yml` and `release.yml` workflows build and test on
Windows, then publish the same wheel and sdist through OIDC in a restricted job.
The PyPI workflow also checks that the tag matches the package version and that
the tagged commit is on `main`. The `v0.1.0` GitHub Actions run succeeded and
published a wheel and sdist through OIDC. A fresh Python 3.13 environment
installed `matnocr==0.1.0` from PyPI with current dependencies, and the full
synthetic-PDF CLI smoke test passed, including real Windows OCR.

### 36. Test PyPI installation

Later:

```powershell
uv tool install matnocr
```

and:

```powershell
pipx install matnocr
```

- [ ] `uv tool`
- [ ] pipx
- [ ] pip

A fresh-environment installation with `uv pip install` from the public PyPI
index and a complete CLI smoke test passed on Python 3.13. The three listed
installation methods remain to be checked separately.

## Phase 8 – GitHub Releases / Windows Distribution

### 37. Evaluate PyInstaller

- [ ] Build `onedir`
- [ ] Build `onefile`
- [ ] Compare startup time
- [ ] Compare file size
- [ ] Check WinRT compatibility
- [ ] Check PDF renderer binaries
- [ ] Test on a clean Windows PC or VM

### 38. GitHub Release Assets

Planned:

```text
matnocr-windows-x64.zip
matnocr-windows-x64.exe
Python wheel
sdist
SHA256SUMS.txt
```

- [ ] Generate release notes
- [ ] Create checksums
- [ ] Upload artifacts automatically

### 39. Release Workflow

Trigger:

```text
git tag v0.1.0
```

Pipeline:

```text
test
→ build Python package
→ build Windows executable
→ publish PyPI
→ create GitHub Release
```

- [ ] Require identical versions everywhere
- [ ] Release only from a tagged commit
- [ ] Do not publish failed builds
- [ ] Attach all release assets, including checksums, to a draft before publishing an immutable release

## Phase 9 – v0.1.0 Release

### 40. Feature Freeze

v0.1 should include:

- [ ] PDF OCR
- [ ] Direct RAM
- [ ] Windows OCR
- [ ] Dynamic languages
- [ ] RTL
- [ ] `--lang`
- [ ] `--pages`
- [ ] `--dpi`
- [ ] `--quality`
- [ ] `--output`
- [ ] `--quiet`
- [ ] `--version`
- [ ] `languages`
- [ ] `doctor`
- [ ] TXT
- [ ] Rich UI
- [ ] Tests
- [ ] GitHub CI
- [ ] PyPI
- [ ] GitHub Release

### 41. Document the v0.1 benchmark

- [ ] 200 DPI
- [ ] 250 DPI
- [ ] 300 DPI
- [ ] Multiple PDF types
- [ ] Multiple languages
- [ ] Document hardware
- [ ] Document pages per second

## Version 0.2 – Planned extensions

### 42. Additional output formats

- [x] Bring simple Markdown forward to v0.1 (page headings and saved default)
- [ ] Add PDF export after the first public release (target v0.2)
- [ ] Text PDF: create a new PDF with visible OCR text, Arabic/RTL rendering, fonts, and page breaks
- [ ] Searchable scan PDF: preserve original pages with an invisible OCR text layer for searching and copying
- [ ] Evaluate the PDF backend and dependencies, including licensing and distribution implications
- [ ] Test both PDF variants with Arabic text and search/copy behavior
- [ ] JSON
- [ ] JSONL
- [ ] Export bounding boxes

### 43. Batch OCR

- [ ] Entire directories
- [ ] Multiple PDFs
- [ ] Output directory
- [ ] A failure in one document should not stop the entire batch

### 44. Resume / Checkpointing

- [ ] Resume processing large books
- [ ] Detect already completed pages
- [ ] Temporary job metadata

### 45. Benchmark Command

Example:

```powershell
matnocr benchmark book.pdf
```

- [ ] Rendering time
- [ ] Bitmap conversion time
- [ ] OCR time
- [ ] Pages per second
- [ ] JSON Benchmark Output

### 46. Improved postprocessing

Optional:

- [ ] `--clean`
- [ ] `--normalize-arabic`
- [ ] BiDi control characters
- [ ] Unicode Normalization
- [ ] ﷺ normalization
- [ ] Obvious artifacts

Important:

- [ ] Raw OCR must remain available

### 47. Alternative OCR Engine

- [ ] Test Tesseract Fast as an optional backend prototype
- [ ] Compare Windows OCR with Tesseract
- [ ] Investigate an optional fallback
- [ ] Build an ensemble only if it measurably improves quality

### 48. Structured book OCR

Evaluate in the long term:

- [ ] Heading detection
- [ ] Footnotes
- [ ] Page numbers
- [ ] Paragraph reconstruction
- [ ] Columns
- [ ] Tables
- [ ] Markdown output

## Version 0.3+ / Long-term ideas

### 49. Native Windows Installer

- [ ] winget package
- [ ] Possible MSI / installer
- [ ] Automatic PATH setup
- [ ] OCR language-pack guidance

### 50. ARM64

- [ ] Test Windows ARM64
- [ ] Check PyWinRT wheels
- [ ] Check the PDF renderer
- [ ] Build a dedicated release asset

### 51. Performance experiments

Only after profiling:

- [ ] Parallel Rendering
- [ ] Pipeline-Prefetch
- [ ] Multiple OCR engines
- [ ] Memory pool
- [ ] Batch Bitmap Conversion

Do not optimize without measuring first.

### 52. Optional GUI

Only in the long term, separate from the CLI:

- [ ] Evaluate a GUI concept
- [ ] Keep the CLI as the core
- [ ] Use the same OCR library for the GUI

## Core principles

Apply these principles to all future decisions:

```text
1. Measure speed; do not guess.
2. Do not silently alter raw OCR.
3. Keep the CLI simple.
4. Keep Windows-native OCR as the core.
5. Treat Arabic as the primary use case.
6. Fully support other Windows OCR languages.
7. Build reproducible releases.
8. Handle open-source licensing correctly.
9. Process large books reliably.
10. Avoid unnecessary complexity in v0.1.
```
