from importlib.metadata import version
from pathlib import Path

import pytest
from typer.testing import CliRunner

from matnocr import cli
from matnocr.cli import app
from matnocr.engine import OcrRunResult

runner = CliRunner()


def test_help_is_available() -> None:
    result = runner.invoke(app, ["--help"])

    assert result.exit_code == 0
    assert "Recognize a scanned PDF with Windows OCR." in result.stdout
    assert "--lang" in result.stdout
    assert "--dpi" in result.stdout
    assert "--quality" in result.stdout
    assert "--output" in result.stdout
    assert "--quiet" in result.stdout
    assert "--version" in result.stdout


def test_pdf_argument_must_exist() -> None:
    result = runner.invoke(app, ["missing.pdf"])

    assert result.exit_code == 2
    assert "does not exist" in result.stderr


def test_invalid_page_selection_is_reported() -> None:
    existing_file = Path(__file__).resolve().parents[2] / "prototype.py"

    result = runner.invoke(app, [str(existing_file), "--pages", "8-3"])

    assert result.exit_code == 2
    assert "Page range must be ascending; got 8-3." in result.stderr


def test_page_count_prints_only_the_number(monkeypatch: pytest.MonkeyPatch) -> None:
    existing_file = Path(__file__).resolve().parents[2] / "prototype.py"
    monkeypatch.setattr("matnocr.cli.get_pdf_page_count", lambda _path: 6)

    result = runner.invoke(app, [str(existing_file), "--page-count"])

    assert result.exit_code == 0
    assert result.stdout == "6\n"


def test_page_count_rejects_page_selection() -> None:
    existing_file = Path(__file__).resolve().parents[2] / "prototype.py"

    result = runner.invoke(
        app,
        [str(existing_file), "--page-count", "--pages", "1"],
    )

    assert result.exit_code == 2
    assert "cannot be combined" in result.stderr
    assert "--page-count" in result.stderr
    assert "--pages" in result.stderr


def test_version_does_not_require_a_pdf() -> None:
    result = runner.invoke(app, ["--version"])

    assert result.exit_code == 0
    assert result.stdout == f"{version('matnocr')}\n"


def test_dpi_and_quality_cannot_be_combined() -> None:
    existing_file = Path(__file__).resolve().parents[2] / "prototype.py"

    result = runner.invoke(
        app,
        [str(existing_file), "--dpi", "200", "--quality", "fast"],
    )

    assert result.exit_code == 2
    assert "--dpi and --quality cannot be combined." in result.stderr


def test_quality_output_and_quiet_options(monkeypatch: pytest.MonkeyPatch) -> None:
    existing_file = Path(__file__).resolve().parents[2] / "prototype.py"
    output_path = Path.cwd() / "chosen-output.txt"
    captured: dict[str, object] = {}

    monkeypatch.setattr(cli, "resolve_language", lambda _language: "ar-SA")

    async def fake_recognize_pdf(
        pdf_path: Path,
        language_tag: str,
        dpi: int,
        **kwargs: object,
    ) -> OcrRunResult:
        captured["dpi"] = dpi
        captured["on_page"] = kwargs["on_page"]
        return OcrRunResult(
            pdf_path=pdf_path,
            language_tag=language_tag,
            dpi=dpi,
            pages=(),
            total_seconds=0.0,
            total_bitmap_seconds=0.0,
            total_ocr_seconds=0.0,
            original_pages=0,
            rendered_pages=0,
        )

    def fake_write_text_output(
        _result: OcrRunResult,
        destination: Path | None,
    ) -> Path:
        captured["output"] = destination
        return destination or output_path

    monkeypatch.setattr(cli, "recognize_pdf", fake_recognize_pdf)
    monkeypatch.setattr(cli, "write_text_output", fake_write_text_output)

    result = runner.invoke(
        app,
        [
            str(existing_file),
            "--quality",
            "fast",
            "--quiet",
            "-o",
            str(output_path),
        ],
    )

    assert result.exit_code == 0
    assert result.stdout == ""
    assert captured == {"dpi": 200, "on_page": None, "output": output_path}
