# MatnOCR – Project

## 1. Project Idea

This project is a very fast, fully local OCR CLI for Windows.

Its goal is to convert scanned PDF books and documents into text directly in
the terminal, with a particular focus on Arabic books and support for all OCR
languages available through the native Windows OCR engine.

The application should:

- run entirely locally
- require no cloud OCR
- work without a GPU
- be very fast
- handle large PDFs
- support multiple languages
- work particularly well with Arabic book pages
- provide a clean, pleasant CLI
- be published as an open-source project on GitHub
- be easy to install through PyPI, `uv tool`, or pipx
- also offer packaged Windows builds through GitHub Releases

## 2. Current Technical Core

### OCR Engine

Text recognition is performed by:

```python
Windows.Media.Ocr
```

Python accesses the native Windows Runtime API through PyWinRT:

```python
from winrt.windows.media.ocr import OcrEngine
```

Advantages:

- very fast local OCR
- no separate large AI model
- Windows manages OCR language packs
- offline operation
- good results with printed Arabic books
- multiple installable languages

### Windows OCR Languages Detected on the Test System

```text
ar-SA
de-DE
tr-TR / tr
```

Windows also supports other OCR languages, including:

```text
bg-BG
bs-LATN-BA
cs-CZ
da-DK
el-GR
en-GB
en-US
es-ES
es-MX
fi-FI
fr-CA
fr-FR
hr-HR
hu-HU
it-IT
ja-JP
ko-KR
nb-NO
nl-NL
pl-PL
pt-BR
pt-PT
ro-RO
ru-RU
sk-SK
sl-SI
sr-CYRL-RS
sr-LATN-RS
sv-SE
zh-CN
zh-HK
zh-TW
```

The application should query the Windows API dynamically for the OCR languages
actually installed, rather than relying on a fixed language list.

## 3. Current Direct-RAM Pipeline

The first version wrote each rendered PDF page to disk as a temporary PNG file.

Previous pipeline:

```text
PDF
→ PyMuPDF
→ RGB
→ PNG encoding
→ temporary file
→ read PNG again
→ BitmapDecoder
→ SoftwareBitmap
→ Windows OCR
```

The current optimized pipeline works directly in RAM:

```text
PDF
→ PDF renderer
→ pixels in RAM
→ SoftwareBitmap
→ Windows OCR
```

This eliminates:

- temporary image files
- SSD writes
- reading image files back from disk
- PNG encoding
- PNG decoding

OCR quality remained practically identical in comparison, while processing
became faster.

## 4. Current PDF Renderer

The selected and implemented renderer is `pypdfium2`, based on PDFium.
According to `TODO.md`, the comparison with PyMuPDF on six Arabic benchmark
pages at 200, 250, and 300 DPI is complete. Rendering, bitmap conversion, OCR
time, total time, and OCR output were compared. OCR quality was practically
on par with PyMuPDF; PDFium also enables the selected permissive Apache-2.0
project license.

The implementation in `src/matnocr/renderer.py` uses two paths:

- **Original scan fast path:** when an embedded image covers at least 70% of the
  PDF page, that image is processed directly at the requested DPI.
- **Fallback:** when there is no suitable scan image, or the fast path encounters
  a runtime error, the complete PDF page is rendered.

Both paths copy BGRA pixels in RAM into a Windows `SoftwareBitmap`.
Neither temporary raster files nor Pillow are required. The PDFium bitmap is
explicitly closed after conversion. In the fast path, the general warning
about closing a foreign bitmap is suppressed specifically because no view of
its buffer is passed to OCR.

Memory usage and wheel size still need to be compared; the roadmap does not
consider these measurements blockers for v0.1. Complete third-party license
files must be included with Windows binary releases.

## 5. Historical Performance Reference

The following values come from the earlier PyMuPDF Direct-RAM prototype,
using a six-page scanned Arabic PDF. They are local historical reference
values, not measurements of the current pypdfium2 package version. According
to `TODO.md`, a release benchmark with documented hardware is still pending.

### 200 DPI – Direct RAM

```text
Pages:      6
Total:      1.685 s
Average:    0.281 s/page
```

Breakdown:

```text
Rendering:  0.040 s/page
Bitmap:     0.015 s/page
OCR:        0.224 s/page
```

### 300 DPI – Direct RAM

```text
Pages:      6
Total:      2.137 s
Average:    0.356 s/page
```

Breakdown:

```text
Rendering:  0.032 s/page
Bitmap:     0.032 s/page
OCR:        0.291 s/page
```

### Previous 300 DPI PNG Pipeline

```text
Average: approx. 0.42 s/page
```

### New Direct-RAM Version

```text
Average: approx. 0.356 s/page
```

Word recognition remained practically identical.

## 6. DPI Modes

The application should support three explicit DPI modes:

```text
200 DPI
250 DPI
300 DPI
```

User-friendly presets should also be available:

```text
fast      -> 200 DPI
balanced  -> 250 DPI
quality   -> 300 DPI
```

Current default:

```text
quality / 300 DPI
```

On the Arabic book pages tested so far, 300 DPI produced better results in
several difficult passages while maintaining very high processing speed.

## 7. Arabic and RTL

Arabic is a particular focus of the project.

Windows OCR returns recognized words with bounding boxes. For RTL languages,
word order is therefore reconstructed from horizontal positions.

Currently designated RTL languages:

```text
ar
fa
ur
he
```

Words are sorted within each recognized line.

By default, MatnOCR preserves the lines recognized by Windows OCR and treats
unusually large vertical gaps as paragraph breaks. The threshold is determined
for each page from word bounding boxes and typical line spacing. This requires
neither a second OCR pass nor a temporary image file. With `--no-layout`,
recognized lines are instead joined with spaces into continuous text.

Highly fragmented OCR results, such as those produced by pages containing only
ornaments or tile patterns, are checked with a targeted 125 DPI pass. Only
suspicious pages receive this additional pass. If the validation pass does not
confirm plausible text in the selected script, the page remains blank in the
output. Recognized words on genuine text pages are not linguistically corrected
or rewritten by this process.

### Example

Windows-internal visual order:

```text
أو العبادات في ركن النية هل الشافعية أصحابنا اختلف الأول
```

Reconstructed:

```text
الأول اختلف أصحابنا الشافعية هل النية ركن في العبادات أو
```

## 8. Current CLI Experience

The application should provide a professional, modern command-line experience.

Implemented stack:

```text
Typer
+
Rich
```

Typer handles:

- argument parsing
- subcommands
- validation
- help
- type-based parameter definitions

Shell completion is currently disabled (`add_completion=False`).

Rich handles:

- progress bars
- tables
- panels
- colors
- status messages
- success and error messages
- clear summaries

The CLI design is consistent across version 0.1:

- Cyan identifies headings and key values.
- Green identifies successful actions.
- Yellow is reserved for warnings, and red for errors.
- OCR settings appear as a compact panel in interactive terminals.
- Help groups input, recognition, and output options and includes usable examples.
- User errors use the consistent format `Error: <message>` and go to `stderr`.
- ANSI colors are disabled in CI, with redirected output, with `NO_COLOR`, or
  when `TERM=dumb`.
- Progress animations run only in interactive terminals; `--quiet` suppresses
  them completely.

### Default Invocation

```powershell
matnocr book.pdf
```

### Explicit Language and DPI

```powershell
matnocr book.pdf --lang ar --dpi 300
```

### Page Range

```powershell
matnocr book.pdf --pages 30-50
```

### Multiple Ranges

```powershell
matnocr book.pdf --pages 1,5,20-35,100
```

### Presets

```powershell
matnocr book.pdf --quality fast
matnocr book.pdf --quality balanced
matnocr book.pdf --quality quality
```

### Custom Output

```powershell
matnocr book.pdf -o output.txt
```

### Quiet Mode for Scripts

```powershell
matnocr book.pdf --quiet
```

### Ignore Layout

```powershell
matnocr book.pdf --no-layout
```

## 9. Current Subcommands

### OCR

Default:

```powershell
matnocr book.pdf
```

### List Languages

```powershell
matnocr languages
```

Example:

```text
Installed OCR languages

✓ ar-SA    Arabic
✓ de-DE    German
✓ tr-TR    Turkish
```

The default language used when `--lang` is omitted is saved for each Windows
user:

```powershell
matnocr languages default ar-SA
```

The language overview explicitly displays the selected default. Windows OCR
language packs can also be managed.

The main `matnocr` help text also shows the configured default language, with
its localized name and technical language code, directly below the project
description. If Arabic is not installed, the help includes the corresponding
installation command.

```powershell
matnocr languages available
matnocr languages install fr-FR
matnocr languages remove fr-FR
```

`languages available` queries the complete list dynamically through
`Get-WindowsCapability` and shows `Installed` or `Not installed` for each
language code. The readable language name comes from
`Windows.Globalization.Language` in the user's Windows display language.
MatnOCR therefore does not need to maintain fixed lists of capability codes
or translations.

Installation and removal use Windows capabilities named
`Language.OCR~~~<tag>~0.0.1.0`. If MatnOCR is not elevated, it opens an
administrative Windows PowerShell through a Windows UAC prompt. After the
operation, the actual capability status is checked again. The active MatnOCR
default language cannot be removed until a different default is selected.

### System Diagnostics

```powershell
matnocr doctor
```

Possible output:

```text
MatnOCR system check

✓ Windows supported
✓ Windows.Media.Ocr available
✓ OCR languages detected
✓ PDF renderer available
✓ Direct-RAM pipeline available
✓ Max OCR image dimension detected

Ready.
```

### Version

```powershell
matnocr --version
```

## 10. Error Handling

The CLI should produce clear errors.

Example when an OCR language is missing:

```text
✗ Russian OCR language is not installed.

Detected OCR languages:
  ar-SA
  de-DE
  tr-TR

Install the Windows Russian OCR language capability and try again.
```

The application should not end with difficult-to-understand Python tracebacks
for ordinary user errors.

## 11. Output Formats

### Version 0.1

TXT remains the initial default output format. At the user's request, simple
Markdown output was brought forward from v0.2 and implemented. It separates
pages with `# Page <PDF page number>` without inferring further book structure.

```powershell
matnocr book.pdf --format md
matnocr book.pdf -o notes.md
matnocr output
matnocr output default md
matnocr output default txt
```

The default output format is saved alongside the default language in the
user-specific `config.json`. Changing either preference preserves the other.
With `-o`, `.txt` selects TXT, while `.md` or `.markdown` selects Markdown,
regardless of the saved default and without regard to case. If the filename
has no extension, the selected format's extension is appended.
`--format txt|md` overrides the default for one invocation; a conflict with the
filename extension produces an error before OCR starts. Other extensions are
rejected.

Existing output files are rejected before OCR starts; only `--force` allows
deliberate replacement. Exclusive file creation during a normal write also
prevents overwriting a file created after the initial check. With `--force`,
a complete temporary text file is written next to the destination before
replacement. Missing output directories, invalid paths, permission errors,
and write failures produce a stderr message and exit code 1 without a
traceback. Output directories are not created automatically. The temporary
text file is not a raster image and does not change the Direct-RAM OCR pipeline.

Automatic filenames use `.txt` or `.md` according to the selected format.
Markdown output is UTF-8 and preserves recognized words and paragraph spacing;
Markdown special characters in OCR text are not escaped.

Normal TXT output contains the lines recognized by Windows OCR and adds a
blank line when vertical line spacing is noticeably larger. With `--no-layout`,
lines are joined into continuous text. Neither mode changes recognized words.

Page markers:

```text
========== Page 1 ==========

...

========== Page 2 ==========
```

### Later Versions

Planned or potential formats:

```text
PDF (text PDF and searchable scan PDF, target v0.2)
JSON
JSONL
```

JSON could later include:

- page number
- line text
- words
- bounding boxes
- language
- DPI
- timing information

## 12. Raw OCR vs. Postprocessing

Default output should remain as close as possible to the actual OCR result.

Automatic linguistic corrections should not happen silently in the background.

Later optional modes could include:

```powershell
--clean
--normalize-arabic
```

Possible features:

- remove Unicode BiDi control characters
- remove obvious artifacts
- optionally normalize `ﷺ`
- clean up whitespace
- clean up lines

Important:

```text
raw OCR
```

and:

```text
postprocessed OCR
```

must remain clearly distinguishable.

## 13. Current Python Project Stack

### Runtime

```text
Python >= 3.11
```

### Package and Project Management

```text
uv
```

### Build Backend

```text
uv_build
```

### CLI

```text
Typer
Rich
```

### OCR

```text
PyWinRT
Windows.Media.Ocr
```

### PDF

```text
pypdfium2 / PDFium
```

### Tests

```text
pytest
coverage.py
```

### Linting / Formatting

```text
Ruff
```

### Type Checking

```text
ty
```

Ruff, ty, pytest, and pytest-cov (coverage.py) are already included in the
`pyproject.toml` development dependency group and recorded in `uv.lock`.
Ruff, ty, pytest, and branch coverage are configured in `pyproject.toml`.
Ruff checks active code and tests; the historical experiments `prototype.py`
and `add_new_white_page.py` are excluded. ty checks `src/` and `tests/` for
Python 3.11 on Windows. The installed PyWinRT types require no global rule
suppression; existing `Any` boundaries for native objects are explained in
`README.md`. Local commands are documented there as well.

## 14. Project Structure and Planned Expansion

```text
project/
├── pyproject.toml
├── uv.lock
├── README.md
├── LICENSE
├── CHANGELOG.md
├── CONTRIBUTING.md
├── SECURITY.md
├── CODE_OF_CONDUCT.md
├── PROJECT.md
├── TODO.md
│
├── src/
│   └── matnocr/
│       ├── __init__.py
│       ├── __main__.py
│       ├── cli.py
│       ├── engine.py
│       ├── renderer.py
│       ├── languages.py
│       ├── pages.py
│       ├── rtl.py
│       ├── output.py
│       ├── config.py
│       ├── doctor.py
│       ├── language_capabilities.py
│       ├── settings.py
│       ├── validation.py
│       └── ui.py
│
├── tests/
│   ├── unit/
│   │   ├── test_pages.py
│   │   ├── test_languages.py
│   │   ├── test_rtl.py
│   │   └── test_output.py
│   │
│   └── integration/
│       ├── test_windows_ocr.py
│       └── test_pdf_renderer.py
│
└── .github/
    ├── ISSUE_TEMPLATE/
    ├── pull_request_template.md
    └── workflows/
        ├── ci.yml
        ├── release.yml
        └── codeql.yml
```

The package lives under `src/matnocr/`; unit tests are in `tests/unit/`, and
integration tests are in `tests/integration/`. The tree also shows planned
files: GitHub workflows are still pending. Community documents, issue forms,
and the pull request template are present. `TODO.md` describes the authoritative
implementation status.

## 15. Packaging and Installation

The project uses `uv_build` and a `src/` layout for its Python package.

Configured console entry point:

```toml
[project.scripts]
matnocr = "matnocr.cli:app"
```

The console entry point launches `matnocr`; `python -m matnocr` is also
available. Full build and wheel verification remains part of the packaging
roadmap.

## 16. Installation for Users

Installation currently uses a local checkout. With uv installed:

```powershell
uv sync --locked
uv run matnocr --help
```

For a standalone CLI command outside the project environment:

```powershell
uv tool install .
```

After changes to the checkout, this kind of tool installation must be updated.
Development changes can be tested directly with `uv run matnocr`.

After a future PyPI publication, `uv tool install matnocr`, `pipx install matnocr`,
and `pip install matnocr` are planned. According to the roadmap, PyPI publishing
and public GitHub releases have not been configured yet.

## 17. Windows Binary / GitHub Release

In addition to the Python package, a ready-to-use Windows build is planned.

Planned:

```text
matnocr-windows-x64.zip
```

and potentially:

```text
matnocr-windows-x64.exe
```

PyInstaller should be evaluated first for version 1.

To evaluate:

```text
PyInstaller onedir
PyInstaller onefile
```

Optional later:

```text
Nuitka
```

The goal is to let ordinary Windows users run the application without installing
Python themselves.

## 18. GitHub and Open Source

The project is intended to be published publicly on GitHub.

Existing repository files:

```text
README.md
LICENSE
CONTRIBUTING.md
CHANGELOG.md
SECURITY.md
CODE_OF_CONDUCT.md
PROJECT.md
TODO.md
```

Also:

```text
.github/
```

with:

- CI workflows
- release workflow
- CodeQL
- issue templates
- pull request template
- Dependabot configuration

## 19. CI – Continuous Integration

CI should run through GitHub Actions.

Because OCR is Windows-specific, at least one Windows runner is required.

Planned workflow for pull requests and pushes:

```text
Checkout
→ setup uv
→ install Python
→ uv sync --locked
→ Ruff check
→ Ruff format --check
→ ty check
→ pytest
→ build wheel/sdist
→ install built package
→ CLI smoke test
```

### Python Matrix

Versions planned for evaluation:

```text
3.11
3.12
3.13
3.14
```

Only versions that work reliably with all WinRT dependencies should be
officially supported.

## 20. Tests

### Unit Tests

These should work independently of installed Windows language packs.

Areas to test:

- page-range parser
- language resolution
- RTL sorting
- output filenames
- presets
- configuration
- CLI validation
- text formatting

### Integration Tests

Located in `tests/integration/`, with the pytest marker `integration`:

- Windows.Media.Ocr availability
- SoftwareBitmap conversion
- real OCR runs
- PDF rendering
- Direct-RAM pipeline
- installed language packs

The tests generate original English, German, and Arabic PDFs in a temporary
test directory. The German and Arabic pages contain only scan images:
Windows System.Drawing renders original text using the local Arial font,
including Arabic letter shaping and RTL. PDFium embeds the images without a
hidden text layer. OCR checks cover umlauts, eszett, and Arabic word order.

Windows-dependent tests skip missing platform or WinRT capabilities;
language-dependent OCR tests skip when their required language pack is absent.
Windows PowerShell, System.Drawing, and Arial must be available to generate
the scans; otherwise, the affected tests also skip. No system languages are
installed, and no font files or private book pages are distributed.
GitHub Windows runners may have different OCR languages from the local system.
Details are in `tests/integration/README.md`.

## 21. Releases

Planned release workflow:

```text
main
↓
Git Tag
↓
v0.x.y
↓
GitHub Actions
↓
Tests
↓
Python Build
↓
Windows Binary Build
↓
PyPI
↓
GitHub Release
```

All artifacts for a version should come from exactly the same Git tag.

## 22. PyPI

The project is intended to be published on PyPI later.

Example:

```powershell
uv tool install matnocr
```

Where possible, PyPI releases should use Trusted Publishing / OIDC so that
long-lived PyPI API tokens do not need to be stored as GitHub secrets.

## 23. GitHub Releases

GitHub Releases should additionally provide:

```text
Python wheel
sdist
Windows x64 binary / zip
checksums
release notes
```

Potentially later:

```text
Windows ARM64
```

## 24. Licensing Strategy

MatnOCR is licensed under **Apache-2.0**. The decision was made after comparing
renderers and is recorded in `LICENSE` and `pyproject.toml`. PyMuPDF is not a
runtime dependency of the package.

Dependencies retain their own licenses. `THIRD_PARTY_NOTICES.md` documents
pypdfium2/PDFium, PyWinRT, Typer, and Rich in particular. Bundled Windows releases
must include the complete PDFium and third-party license files from the
versions actually used.

## 25. Project Name

The naming decision is complete:

```text
Brand:       MatnOCR
PyPI:        matnocr
CLI:         matnocr
Python pkg:  matnocr
GitHub repo: matnocr
Executable:  matnocr.exe
```

The collision checks are recorded as completed in Phase 0 of `TODO.md`.
Selecting the name does not mean publication on GitHub or PyPI has already
happened.

## 26. Positioning

The project should be positioned as more than a simple wrapper around Windows
OCR.

Its specific niche is:

```text
High-performance PDF/book OCR CLI powered by Windows native OCR
```

Distinctive features:

- PDF-first
- book-first
- Arabic-first, but multilingual
- native Windows OCR
- Direct RAM
- RTL reconstruction
- page ranges
- DPI presets
- very high throughput
- fully local
- no GPU
- pleasant CLI
- reproducible benchmarks

## 27. Version 0.1 – Target Scope

The first proper open-source version should remain deliberately compact.

Planned scope:

- PDF input
- Windows OCR
- Direct-RAM pipeline
- dynamic Windows OCR languages
- Arabic / RTL reconstruction
- `--lang`
- `--pages`
- `--dpi`
- `--quality`
- `--output`
- TXT and simple Markdown output with a saved default
- `languages`
- `doctor`
- `--quiet`
- `--version`
- Rich progress
- clear error messages
- Python package
- GitHub CI
- PyPI release
- GitHub Windows release

Not required for v0.1:

- GUI
- AI correction
- Tesseract ensemble
- complex layout reconstruction
- complex Markdown layout reconstruction
- OCR server
- parallel OCR
- batch folder processing

## 28. Version 0.2+ – Potential Extensions

### Extended Output

Simple Markdown with page headings is already available in v0.1.
Further goals:

- PDF export for version 0.2 after the first public release:
  - A text PDF with visible OCR text, suitable fonts, Arabic/RTL rendering,
    and page breaks.
  - A searchable scan PDF with original pages and an invisible OCR text layer
    for searching and copying.
- JSON
- JSONL
- bounding boxes

Both PDF variants require evaluation of the backend and licensing implications,
text positions, fonts, and Arabic search/copy behavior. PDF export has not been
implemented and should not change the existing Direct-RAM OCR pipeline.

### Batch Processing

```powershell
matnocr batch ./books
```

### Resume

Continue interrupted OCR jobs for large books.

### Benchmark Command

```powershell
matnocr benchmark book.pdf
```

### Renderer Benchmark

The initial PyMuPDF/PDFium comparison is complete. Further measurements of
memory usage and wheel size, along with repeatable release benchmarks,
remain planned.

### Alternative OCR Engines

Optional:

- Tesseract
- Windows OCR + Tesseract ensemble
- fallback engine for difficult pages

### Arabic Postprocessing

Optional:

- ﷺ normalization
- BiDi cleanup
- Unicode normalization
- artifact detection

### Structured Output

- headings
- footnotes
- page numbers
- paragraphs
- tables

## 29. Benchmark Rules

Performance comparisons should be reproducible.

Document the following for each test:

- PDF
- page count
- DPI
- CPU
- Windows version
- Python version
- renderer
- OCR engine
- rendering time
- bitmap time
- OCR time
- total time
- average time per page

Copyrighted test pages should not be added to the public repository without
permission.

CI tests should instead use original or public-domain test documents.

## 30. Long-Term Vision

The long-term goal is an open-source Windows CLI that lets a user run, for
example:

```powershell
matnocr kitab.pdf --lang ar --pages 30-100
```

and receive a clean text file within a short time.

The project should combine the simplicity of a modern CLI with the speed of
the native Windows OCR engine.

Long-term core principles:

```text
fast
local
simple
transparent
multilingual
scriptable
open source
```
