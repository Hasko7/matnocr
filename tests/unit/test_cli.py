from pathlib import Path

import pytest
from typer.testing import CliRunner

from matnocr.cli import app

runner = CliRunner()


def test_help_is_available() -> None:
    result = runner.invoke(app, ["--help"])

    assert result.exit_code == 0
    assert "Recognize a scanned PDF with Windows OCR." in result.stdout
    assert "--lang" in result.stdout
    assert "--dpi" in result.stdout


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
