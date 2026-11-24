# Contributing to MatnOCR

Contributions that improve reliability, OCR output, documentation, and the
Windows command-line experience are welcome. Please follow the
[Code of Conduct](CODE_OF_CONDUCT.md).

## Before You Start

Read [PROJECT.md](PROJECT.md) for the architecture, [TODO.md](TODO.md) for
priorities, and [AGENTS.md](AGENTS.md) for repository working rules. For larger
features or changes to the renderer, OCR engine, dependencies, or packaging,
open a feature request before implementation so the scope can be discussed.

MatnOCR is in development. The package version is not evidence of a published
release; see [CHANGELOG.md](CHANGELOG.md). The CI workflow is configured in
`.github/workflows/ci.yml`; publishing remains planned work.

## Report an Issue

Use the appropriate GitHub issue form once this repository is published:

- **Bug report:** crashes, invalid behavior, installation, CLI, or output errors.
- **Feature request:** a concrete problem and the behavior that would solve it.
- **OCR quality report:** incorrect recognition, word order, or layout. Include
  the language, Windows version, DPI, PDF type, affected pages, expected text,
  and actual unedited OCR output.

Search existing issues first. Supply a minimal reproducer where possible, and
remove personal paths, secrets, and private document contents from diagnostics.
Only share samples you have permission to publish. Synthetic or public-domain
examples are preferred. For vulnerabilities, follow [SECURITY.md](SECURITY.md)
instead of posting exploit details in a public issue.

## Local Development

Use Windows, Python 3.11 or later, and uv:

```powershell
uv sync --locked
uv run matnocr --help
uv run matnocr doctor
```

For a source-linked CLI installation, use `uv tool install --editable .`.
See [the development guide](docs/development.md) for details.

Before submitting a change, run:

```powershell
uv run ruff check .
uv run ruff format --check .
uv run ty check
uv run pytest
```

Apply formatting with `uv run ruff format .`. Unit tests live in `tests/unit/`;
real runtime tests live in `tests/integration/` and use the `integration` marker.
Run them separately with `uv run pytest -m integration` or
`uv run pytest -m "not integration"`. Missing language capabilities skip the
corresponding integration tests; mention relevant skips in your PR. Do not
install or remove system language packs from tests.

Ruff and ty intentionally exclude historical experiments from their normal
scope. See the configuration in `pyproject.toml` and the development guide.

## Keep Changes Focused

- Add or update tests for new core behavior and fixed regressions.
- Preserve the Direct-RAM OCR pipeline and dynamic Windows language discovery.
- Preserve recognized words. Do not silently correct spelling or normalize Arabic.
- Test Arabic/RTL changes with positions and real examples; never reverse an
  entire page string to fix word order.
- Measure before and after changes to rendering, bitmap conversion, memory
  management, preprocessing, or concurrency. Record the input, DPI, hardware,
  software versions, timing, and any OCR output differences.
- Check dependency licenses before adding runtime dependencies. Preserve
  Apache-2.0 licensing and the third-party distribution notices.
- Keep private PDFs, generated output, and unrelated changes out of the PR.

## Submit a Pull Request

Fork the repository if needed and work on a branch. Describe the problem,
resulting behavior, and validation in the PR template. For visual CLI changes,
include a screenshot; for OCR changes, include a shareable input/output example.

Update relevant documentation, add a concise entry under `Unreleased` in
[CHANGELOG.md](CHANGELOG.md), and update [TODO.md](TODO.md) when a roadmap item
is completed. Explain any checks you could not run. Do not change release
versions or introduce a new release process as part of an unrelated fix.

Contribute only material you are entitled to share under the project's
[Apache-2.0 license](LICENSE), with third-party notices where applicable.
