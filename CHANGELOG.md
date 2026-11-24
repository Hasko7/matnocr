# Changelog

This file records notable user-facing changes. Entries under `Unreleased` are
development work, not a claim that a public release has been published.

## Unreleased

### Added

- Repository safeguards requiring CI before merging into `main`, protecting
  version tags from updates/deletion, and enabling immutable future releases.
- Windows-native PDF OCR through PDFium and `Windows.Media.Ocr`, with a
  Direct-RAM pipeline and a fast path for embedded scan images.
- Dynamic OCR language discovery, short language-code resolution, saved default
  language, and Windows OCR language pack management.
- Page ranges, page counts, 200/250/300 DPI quality presets, Rich progress,
  quiet mode, version output, and system diagnostics.
- UTF-8 TXT and Markdown exports, original PDF page markers, a saved default
  output format, and format selection through filename extensions or `--format`.
- Position-based RTL word ordering, line preservation, paragraph spacing, and
  `--no-layout` for continuous text.
- Low-resolution validation for suspicious non-text OCR results.
- Output overwrite protection with `--force` for deliberate replacement and
  staged writes that preserve existing exports if replacement fails.
- Unit tests, synthetic English/German/Arabic integration documents, and local
  Ruff, ty, pytest, and coverage configuration.
- GitHub Actions CI for Python 3.11–3.14 on Windows Server 2025, including
  locked dependencies, code checks, capability-aware integration tests, package
  builds, and CLI smoke tests in a fresh wheel environment. A combined `CI`
  check reports the overall matrix result for branch protection.
- Usage and development documentation, screenshots, contributor guidance,
  security and conduct policies, and GitHub issue and pull request templates.

### Fixed

- Suppressed the PDFium foreign-bitmap close warning in the scan fast path
  after verifying that OCR uses an independent pixel copy.

Public PyPI releases and packaged Windows releases are still planned.
