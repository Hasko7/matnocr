from importlib.metadata import version
from pathlib import Path

import pytest
from typer.testing import CliRunner

from matnocr import cli
from matnocr.cli import app
from matnocr.config import OutputFormat
from matnocr.doctor import DiagnosticCheck
from matnocr.engine import OcrRunResult
from matnocr.language_capabilities import (
    CapabilityCatalogResult,
    LanguageCapabilityResult,
    OcrCapability,
)
from matnocr.languages import LanguageNotInstalledError, OcrLanguage

runner = CliRunner()


@pytest.fixture(autouse=True)
def isolated_settings(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("MATNOCR_CONFIG_HOME", str(tmp_path))


def test_help_is_available() -> None:
    result = runner.invoke(app, ["--help"])

    assert result.exit_code == 0
    assert "Fast local OCR for scanned Arabic PDFs" in result.stdout
    assert "support for many other" in result.stdout
    assert "languages." in result.stdout
    assert "ocr" in result.stdout
    assert "languages" in result.stdout
    assert "doctor" in result.stdout
    assert "--version" in result.stdout

    ocr_help = runner.invoke(app, ["ocr", "--help"])

    assert ocr_help.exit_code == 0
    assert "Convert a scanned PDF into text." in ocr_help.stdout
    assert "--lang" in ocr_help.stdout
    assert "--dpi" in ocr_help.stdout
    assert "--quality" in ocr_help.stdout
    assert "--output" in ocr_help.stdout
    assert "--quiet" in ocr_help.stdout
    assert "--no-layout" in ocr_help.stdout
    assert "Input" in ocr_help.stdout
    assert "Recognition" in ocr_help.stdout
    assert "Output" in ocr_help.stdout
    assert "Examples" in ocr_help.stdout
    assert "matnocr book.pdf --lang ar-SA" in ocr_help.stdout


def test_help_has_no_ansi_escape_sequences_in_ci(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("CI", "true")

    result = runner.invoke(app, ["--help"], color=True)

    assert result.exit_code == 0
    assert "\x1b[" not in result.stdout


def test_root_help_shows_current_default_language(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(cli, "load_default_language", lambda: "ar")
    monkeypatch.setattr(cli, "resolve_language", lambda _tag: "ar-SA")
    monkeypatch.setattr(
        cli,
        "get_language_display_name",
        lambda _tag: "Arabic (Saudi Arabia)",
    )

    result = runner.invoke(app, ["--help"])

    assert result.exit_code == 0
    assert "Default OCR language: Arabic (Saudi Arabia) (ar-SA)" in result.stdout
    assert "Install Arabic OCR" not in result.stdout
    assert "Set Arabic as default" not in result.stdout


def test_root_help_suggests_installing_arabic_when_missing(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(cli, "load_default_language", lambda: "de-DE")

    def resolve_test_language(tag: str) -> str:
        if tag == "ar":
            raise LanguageNotInstalledError("Arabic is not installed")
        return "de-DE"

    monkeypatch.setattr(cli, "resolve_language", resolve_test_language)
    monkeypatch.setattr(
        cli,
        "get_language_display_name",
        lambda _tag: "German (Germany)",
    )

    result = runner.invoke(app, ["--help"])

    assert result.exit_code == 0
    assert "Default OCR language: German (Germany) (de-DE)" in result.stdout
    assert "matnocr languages install ar-SA" in result.stdout


def test_root_help_does_not_suggest_selecting_installed_arabic(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(cli, "load_default_language", lambda: "de-DE")
    monkeypatch.setattr(
        cli,
        "resolve_language",
        lambda tag: "ar-SA" if tag == "ar" else "de-DE",
    )
    monkeypatch.setattr(
        cli,
        "get_language_display_name",
        lambda _tag: "German (Germany)",
    )

    result = runner.invoke(app, ["--help"])

    assert result.exit_code == 0
    assert "Set Arabic as default" not in result.stdout
    assert "matnocr languages default ar-SA" not in result.stdout


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
        captured["on_start"] = kwargs["on_start"]
        captured["on_page"] = kwargs["on_page"]
        captured["preserve_layout"] = kwargs["preserve_layout"]
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
        *,
        output_format: OutputFormat,
        force: bool,
    ) -> Path:
        assert output_format == OutputFormat.TXT
        assert force is False
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
    assert captured == {
        "dpi": 200,
        "on_start": None,
        "on_page": None,
        "preserve_layout": True,
        "output": output_path,
    }

    captured.clear()
    no_layout_result = runner.invoke(
        app,
        [
            str(existing_file),
            "--quality",
            "fast",
            "--quiet",
            "--no-layout",
            "-o",
            str(output_path),
        ],
    )

    assert no_layout_result.exit_code == 0
    assert captured["preserve_layout"] is False


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
    assert "Default OCR language: ar-SA" in result.stdout
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


def test_install_language_command_opens_administrator_operation(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        cli,
        "manage_language_capability",
        lambda action, tag: LanguageCapabilityResult(tag, action, True),
    )

    result = runner.invoke(app, ["languages", "install", "fr-FR"])

    assert result.exit_code == 0
    assert "Administrator permission is required" in result.stdout
    assert "OCR language fr-FR installed" in result.stdout


def test_available_languages_command_shows_installation_states(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        cli,
        "get_language_capabilities",
        lambda: CapabilityCatalogResult(
            (
                OcrCapability("ar-SA", "Installed", "Arabic (Saudi Arabia)"),
                OcrCapability("fr-FR", "NotPresent", "French (France)"),
            ),
            True,
        ),
    )

    result = runner.invoke(app, ["languages", "available"])

    assert result.exit_code == 0
    assert "Available Windows OCR" in result.stdout
    assert "language capabilities" in result.stdout
    assert "ar-SA" in result.stdout
    assert "Arabic (Saudi Arabia)" in result.stdout
    assert "Installed" in result.stdout
    assert "fr-FR" in result.stdout
    assert "French (France)" in result.stdout
    assert "Not installed" in result.stdout
    assert "matnocr languages install" in result.stdout
    assert "<code>" in result.stdout


def test_install_language_requires_a_code_from_available_list() -> None:
    result = runner.invoke(app, ["languages", "install", "fr"])

    assert result.exit_code == 1
    assert "complete language code" in result.stderr
    assert "matnocr languages available" in result.stderr
    assert "matnocr languages install <code>" in result.stderr


def test_remove_default_language_is_rejected(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    called = False
    monkeypatch.setattr(cli, "load_default_language", lambda: "fr-FR")

    def fake_manage(_action: str, _tag: str) -> None:
        nonlocal called
        called = True

    monkeypatch.setattr(cli, "manage_language_capability", fake_manage)

    result = runner.invoke(app, ["languages", "remove", "fr-FR"])

    assert result.exit_code == 1
    assert "Cannot remove the default OCR language fr-FR" in result.stderr
    assert not called


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


def test_output_write_failure_is_a_clean_stderr_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    existing_file = Path(__file__).resolve().parents[2] / "prototype.py"
    monkeypatch.setattr(cli, "resolve_language", lambda _language: "ar-SA")

    async def fake_recognize_pdf(
        pdf_path: Path,
        language_tag: str,
        dpi: int,
        **_kwargs: object,
    ) -> OcrRunResult:
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

    def fail_to_write(
        _result: OcrRunResult, _destination: Path | None, **_kwargs: object
    ) -> Path:
        raise PermissionError("access denied")

    monkeypatch.setattr(cli, "recognize_pdf", fake_recognize_pdf)
    monkeypatch.setattr(cli, "write_text_output", fail_to_write)

    result = runner.invoke(app, [str(existing_file), "--quiet"])

    assert result.exit_code == 1
    assert result.stdout == ""
    assert "Error: Could not write the OCR output: access denied" in result.stderr
    assert "Traceback" not in result.stderr


def test_output_default_can_be_set_and_displayed() -> None:
    assert "Default output format: txt" in runner.invoke(app, ["output"]).stdout
    result = runner.invoke(app, ["output", "default", "md"])
    assert result.exit_code == 0
    assert "Default output format: md" in result.stdout
    assert "Default output format: md" in runner.invoke(app, ["output"]).stdout
    assert runner.invoke(app, ["output", "default", "pdf"]).exit_code == 2


@pytest.mark.parametrize("args", [["output"], ["output", "--help"]])
def test_output_overview_explains_formats_and_usage(args: list[str]) -> None:
    result = runner.invoke(app, args)
    assert result.exit_code == 0
    for text in (
        "Available formats:",
        "Plain text (.txt)",
        "Markdown (.md or .markdown)",
        "# Page x",
        "matnocr output default txt",
        "matnocr output default md",
        "matnocr book.pdf --format md",
        "matnocr book.pdf -o notes.md",
        "matnocr book.pdf -o notes.txt",
        "extension overrides the saved default",
    ):
        assert text in result.stdout


@pytest.mark.parametrize(
    ("default", "filename", "extra", "expected"),
    [
        ("txt", None, [], "txt"),
        ("md", None, [], "md"),
        ("txt", "notes.md", [], "md"),
        ("md", "notes.txt", [], "txt"),
        ("txt", None, ["--format", "md"], "md"),
        ("md", "notes", [], "md"),
        ("txt", "notes.txt", ["--force"], "txt"),
    ],
)
def test_cli_exports_selected_format(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    default: str,
    filename: str | None,
    extra: list[str],
    expected: str,
) -> None:
    from matnocr.engine import OcrPageResult, PageTiming
    from matnocr.settings import save_default_output_format

    save_default_output_format(OutputFormat(default))
    source = tmp_path / "book.pdf"
    source.touch()
    monkeypatch.setattr(cli, "resolve_language", lambda _tag: "ar-SA")

    async def fake_recognize(*_args: object, **_kwargs: object) -> OcrRunResult:
        return OcrRunResult(
            source,
            "ar-SA",
            300,
            (OcrPageResult(9, "نص عربي", 100, 100, "ORIGINAL", PageTiming(0, 0, 0)),),
            0,
            0,
            0,
            1,
            0,
        )

    monkeypatch.setattr(cli, "recognize_pdf", fake_recognize)
    args = [str(source), "--quiet", *extra]
    if filename is not None:
        args.extend(["-o", str(tmp_path / filename)])
        if "--force" in extra:
            (tmp_path / filename).write_text("previous export", encoding="utf-8")
    result = runner.invoke(app, args)
    assert result.exit_code == 0, result.output
    assert result.stdout == ""
    target = tmp_path / (filename or f"book_matnocr_ar_300dpi.{expected}")
    if not target.suffix:
        target = target.with_suffix(f".{expected}")
    text = target.read_text(encoding="utf-8")
    assert "نص عربي" in text
    assert ("# Page 9" if expected == "md" else "========== Page 9 ==========") in text


@pytest.mark.parametrize(
    "options", [["-o", "notes.pdf"], ["-o", "notes.md", "--format", "txt"]]
)
def test_invalid_output_format_is_rejected_before_ocr(options: list[str]) -> None:
    source = Path(__file__).resolve().parents[2] / "prototype.py"
    result = runner.invoke(app, [str(source), *options])
    assert result.exit_code == 2
    assert "--format/--output" in result.stderr
    assert "Traceback" not in result.stderr


@pytest.mark.parametrize("automatic", [False, True])
def test_existing_output_is_rejected_before_ocr(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, automatic: bool
) -> None:
    source = tmp_path / "book.pdf"
    source.touch()
    destination = tmp_path / (
        "book_matnocr_ar_300dpi.txt" if automatic else "existing.txt"
    )
    destination.write_text("keep this", encoding="utf-8")
    monkeypatch.setattr(cli, "resolve_language", lambda _tag: "ar-SA")

    async def unexpected_ocr(*_args: object, **_kwargs: object) -> None:
        pytest.fail("OCR must not start for an existing output")

    monkeypatch.setattr(cli, "recognize_pdf", unexpected_ocr)
    args = [str(source), "--quiet"]
    if not automatic:
        args.extend(["-o", str(destination)])
    result = runner.invoke(app, args)
    assert result.exit_code == 1
    assert result.stdout == ""
    assert "--force" in result.stderr
    assert destination.read_text(encoding="utf-8") == "keep this"


def test_invalid_output_parent_is_a_clean_error(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    source = tmp_path / "book.pdf"
    source.touch()
    monkeypatch.setattr(cli, "resolve_language", lambda _tag: "ar-SA")
    result = runner.invoke(
        app, [str(source), "-o", str(tmp_path / "missing" / "out.txt"), "--quiet"]
    )
    assert result.exit_code == 1
    assert "Output directory does not exist" in result.stderr
    assert "Traceback" not in result.stderr
