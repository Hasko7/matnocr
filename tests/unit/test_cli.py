from importlib.metadata import version
from pathlib import Path

import pytest
from typer.testing import CliRunner

from matnocr import cli
from matnocr.cli import app
from matnocr.doctor import DiagnosticCheck
from matnocr.engine import OcrRunResult
from matnocr.languages import LanguageNotInstalledError, OcrLanguage

runner = CliRunner()


def test_help_is_available() -> None:
    result = runner.invoke(app, ["--help"])

    assert result.exit_code == 0
    assert "Fast local PDF OCR powered by Windows." in result.stdout
    assert "ocr" in result.stdout
    assert "languages" in result.stdout
    assert "doctor" in result.stdout
    assert "--version" in result.stdout

    ocr_help = runner.invoke(app, ["ocr", "--help"])

    assert ocr_help.exit_code == 0
    assert "Recognize a scanned PDF with Windows OCR." in ocr_help.stdout
    assert "--lang" in ocr_help.stdout
    assert "--dpi" in ocr_help.stdout
    assert "--quality" in ocr_help.stdout
    assert "--output" in ocr_help.stdout
    assert "--quiet" in ocr_help.stdout


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


def test_languages_command_shows_installed_languages(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(cli, "load_default_language", lambda: "ar-SA")
    monkeypatch.setattr(
        cli,
        "get_available_languages",
        lambda: (
            OcrLanguage("ar-SA", "Arabic (Saudi Arabia)", "Arabic"),
            OcrLanguage("de-DE", "German (Germany)", "Deutsch"),
        ),
    )

    result = runner.invoke(app, ["languages"])

    assert result.exit_code == 0
    assert "Installed Windows OCR languages" in result.stdout
    assert "ar-SA" in result.stdout
    assert "Arabic (Saudi Arabia)" in result.stdout
    assert "Default" in result.stdout
    assert "de-DE" in result.stdout


def test_missing_ocr_language_has_an_actionable_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    existing_file = Path(__file__).resolve().parents[2] / "prototype.py"
    monkeypatch.setattr(cli, "load_default_language", lambda: "en")

    def missing_language(_requested: str) -> str:
        raise LanguageNotInstalledError(
            "OCR language 'en' is not installed. Install it through Windows Settings."
        )

    monkeypatch.setattr(cli, "resolve_language", missing_language)

    result = runner.invoke(app, [str(existing_file)])

    assert result.exit_code == 2
    assert "OCR language" in result.stderr
    assert "Windows Settings" in result.stderr
    assert "Traceback" not in result.stderr


def test_default_language_command(monkeypatch: pytest.MonkeyPatch) -> None:
    settings_path = Path.cwd() / "config.json"
    monkeypatch.setattr(cli, "resolve_language", lambda _tag: "en-US")
    monkeypatch.setattr(cli, "save_default_language", lambda _tag: settings_path)

    result = runner.invoke(app, ["languages", "default", "en"])

    assert result.exit_code == 0
    assert "Default OCR language: en-US" in result.stdout
    assert str(settings_path) in result.stdout


def test_doctor_command_reports_success(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        cli,
        "run_doctor_checks",
        lambda: (DiagnosticCheck("Windows.Media.Ocr", True, "Available"),),
    )

    result = runner.invoke(app, ["doctor"])

    assert result.exit_code == 0
    assert "MatnOCR system check" in result.stdout
    assert "Windows.Media.Ocr" in result.stdout
    assert "Ready" in result.stdout
