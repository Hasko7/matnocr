# MatnOCR

Fast, local PDF OCR for Windows, with a focus on Arabic books and support for
the Windows OCR languages installed on your system. Text recognition runs
offline, without a cloud service or GPU.

MatnOCR is under development. The OCR CLI is implemented; GitHub CI, PyPI
publishing, and packaged Windows releases are still planned.
See [TODO.md](TODO.md) for the detailed status.

## Features

- PDFium rendering through `pypdfium2`, with a fast path for embedded scans.
- Direct-RAM pipeline to `Windows.Media.Ocr`, without temporary raster files.
- Position-based word ordering for Arabic and other RTL languages.
- Page ranges, three quality presets, and UTF-8 TXT output with page markers.
- Line and paragraph spacing, or continuous text with `--no-layout`.
- Dynamic OCR language discovery, a saved default language, and language pack management.
- Rich progress display, `--quiet`, system diagnostics, and clear error messages.

## Requirements and Installation

You need Windows with the `Windows.Media.Ocr` API available, Python 3.11 or
later, uv, and the appropriate Windows OCR language pack. Full validation of
the planned Python version matrix is still pending.

Install and run from the local repository:

```powershell
uv sync --locked
uv run matnocr --help
uv run matnocr doctor
```

Optionally, install a standalone CLI command from this checkout:

```powershell
uv tool install .
matnocr --help
```

This tool installation uses its own environment. After source changes,
reinstall it from the same checkout:

```powershell
uv tool install --reinstall .
```

For development, `uv run matnocr` uses the project environment directly.
You can also use `uv run python -m matnocr`. Installation from PyPI with
`uv tool install matnocr`, pipx, or pip is planned after the public release.

## Quick Start

```powershell
uv run matnocr languages
uv run matnocr book.pdf --lang ar --pages 1-10
```

After installing the tool, these commands are equivalent:

```powershell
matnocr book.pdf
matnocr ocr book.pdf
```

Without `--lang`, MatnOCR uses the saved default language, initially Arabic
(`ar`). The default resolution is 300 DPI. The automatic output filename is,
for example, `book_matnocr_ar_300dpi.txt`, saved next to the PDF.

Example completion output (illustrative values):

```text
2 pages · 1.1s · 1.82 pages/s
✓ Saved to C:\Books\book_matnocr_ar_300dpi.txt
```

## Pages and Quality

```powershell
matnocr book.pdf --pages 30-50
matnocr book.pdf --pages 1,5,20-35,100
matnocr book.pdf --page-count
matnocr book.pdf --quality fast
matnocr book.pdf --dpi 250
```

Page numbers refer to physical PDF pages starting at 1, regardless of printed
book page numbers. Duplicates are removed, and pages are processed in ascending
order. `--page-count` prints only the total page count and cannot be combined
with `--pages`.

| Preset | DPI |
| --- | --- |
| `fast` | 200 |
| `balanced` | 250 |
| `quality` (default) | 300 |

`--dpi` accepts 200, 250, or 300 and cannot be combined with `--quality`.
125 DPI is used only internally to validate suspected non-text pages.

## Languages and Windows OCR Language Packs

```powershell
matnocr languages
matnocr languages default ar-SA
matnocr book.pdf --lang de
matnocr languages available
matnocr languages install fr-FR
matnocr languages remove fr-FR
```

Installed OCR languages are queried through Windows. Short codes such as `ar`
or `de` resolve to a matching installed tag such as `ar-SA` or `de-DE`.
The saved default language appears in the language list and the main help text.

`languages available` queries the Windows capability catalog dynamically.
Installation and removal require administrator privileges; when needed,
MatnOCR opens PowerShell through a Windows UAC prompt. Querying the catalog
may also require administrator approval. Installing language packs may require
a download; subsequent OCR runs work offline. To remove the active default
language, select another default first.

The default language is saved in `%LOCALAPPDATA%\MatnOCR\config.json`.
Set `MATNOCR_CONFIG_HOME` to override the configuration directory.

## Output and Scripting

```powershell
matnocr book.pdf -o result.txt
matnocr book.pdf --no-layout
matnocr book.pdf --quiet
```

TXT output uses UTF-8 and markers such as `========== Page 1 ==========`.
By default, OCR lines are preserved, and unusually large vertical gaps produce
blank lines. `--no-layout` joins lines with spaces. Recognized words are not
linguistically corrected or normalized.

Highly fragmented results may come from ornaments rather than text. Only
these suspicious pages receive a second OCR pass at 125 DPI. If that pass does
not confirm plausible text, the page is left blank in the output.

`--quiet` suppresses progress and the completion summary. Recognized text is
written to the output file; errors go to stderr. Invalid arguments return a
nonzero exit status; runtime and write errors return exit code 1. Progress
animations run only in interactive terminals. Colors are disabled in CI,
with `NO_COLOR`, and in other environments that do not support them.

## Current Limitations

- The OCR runtime is Windows-specific and requires installed language packs.
- Existing output files are currently overwritten, including automatically
  named output files. Overwrite protection is still planned.
- Images exceeding the maximum Windows OCR dimensions produce an error;
  automatic splitting is not implemented.
- Word ordering and paragraph spacing do not replace complex layout analysis
  for columns, tables, or footnotes. Non-text detection is also heuristic.
- JSON/Markdown output, batch processing, resume support, parallel OCR, and
  a GUI are not implemented yet.

## Benchmarks

Historical local results from the earlier **PyMuPDF Direct-RAM prototype**,
using a six-page scanned Arabic PDF:

| Resolution | Total time | Time per page |
| --- | --- | --- |
| 200 DPI | 1.685 s | 0.281 s |
| 300 DPI | 2.137 s | 0.356 s |

These values do not measure the current pypdfium2 package version and are not
a general performance guarantee. According to the roadmap, the renderer
comparison at 200/250/300 DPI is complete; pypdfium2 was selected with
practically comparable OCR quality. Memory usage, wheel size, and a complete
release benchmark with hardware details remain pending.
See [PROJECT.md](PROJECT.md) for more background.

## Development and Contributing

Before making substantial changes, read [AGENTS.md](AGENTS.md),
[PROJECT.md](PROJECT.md), and [TODO.md](TODO.md). Keep changes small and easy
to review, cover Arabic/RTL examples, and measure performance before and after
pipeline changes. Do not add private book pages as public test data; prefer
synthetic or public-domain documents.

The development dependency group already includes Ruff, ty, pytest, and
pytest-cov. Local commands:

```powershell
uv sync --locked
uv run pytest tests/unit
uv run pytest --cov=matnocr tests/unit
uv run ruff check .
uv run ruff format --check .
uv run ty check
```

To apply formatting, run `uv run ruff format .`.
These commands describe the intended verification workflow, not a claim that
all checks already pass. Project-specific tool configuration, integration
tests, and CI remain open roadmap items. The tests also import Windows
components and should currently be run on Windows.

## License

MatnOCR is licensed under [Apache-2.0](LICENSE). Dependencies retain their own
licenses; see [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).
Bundled Windows releases must also include the complete PDFium and third-party
license files from the builds used.
