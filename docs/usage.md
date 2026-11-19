# Usage Guide

[Back to the README](../README.md)

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

TXT is the initial default and uses UTF-8 with markers such as
`========== Page 1 ==========`. Markdown uses headings with the original PDF
page numbers:

```markdown
# Page 9

Recognized text from page 9.

# Page 10

Recognized text from page 10.
```

Choose the format for one run, or save your preferred default:

```powershell
matnocr book.pdf --format md
matnocr book.pdf -o notes.md
matnocr output
matnocr output default md
matnocr output default txt
```

`matnocr output` displays the saved default, available formats, and usage
examples. The same guide is available with `matnocr output --help`.
Without `--format` or a filename
extension, this default determines both the content and automatic extension
(`.txt` or `.md`). The preference is stored alongside the default language in
`config.json`; changing one preference preserves the other.

An explicit `-o` extension takes precedence over the saved default: `.md` and
`.markdown` select Markdown, while `.txt` selects TXT (case-insensitive).
A filename without an extension receives the extension of the selected format.
`--format txt` or `--format md` overrides the saved default for a single run.
If `--format` conflicts with the filename extension, MatnOCR reports an error
before OCR starts. Other extensions, including `.pdf`, are not supported yet.

Both output formats preserve the recognized words without interpreting book
headings, lists, or other document structure. Only page headings are added to
Markdown; characters that have Markdown meaning in the OCR text are not escaped.
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

Existing output files are protected by default, including automatically named
exports. MatnOCR reports the conflict before OCR starts. To replace one
explicitly:

```powershell
matnocr book.pdf -o notes.md --force
```

The destination directory must already exist. Invalid paths, permissions, and
locked files produce a clear stderr error with exit code 1, without a traceback.
With `--force`, MatnOCR writes a temporary text file beside the destination and
replaces the old export only after the write succeeds. This does not add any
temporary raster files to the OCR pipeline.


