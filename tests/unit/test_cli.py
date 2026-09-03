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
