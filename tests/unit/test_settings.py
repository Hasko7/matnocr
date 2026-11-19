import tempfile
from pathlib import Path

import pytest

from matnocr.config import OutputFormat
from matnocr.settings import (
    SettingsError,
    load_default_language,
    load_default_output_format,
    save_default_language,
    save_default_output_format,
)


def test_missing_settings_use_arabic_default() -> None:
    with tempfile.TemporaryDirectory(dir=Path.cwd()) as directory:
        settings_path = Path(directory) / "config.json"

        assert load_default_language(settings_path) == "ar"


def test_default_language_is_persisted() -> None:
    with tempfile.TemporaryDirectory(dir=Path.cwd()) as directory:
        settings_path = Path(directory) / "nested" / "config.json"

        written_path = save_default_language("en-US", settings_path)

        assert written_path == settings_path
        assert load_default_language(settings_path) == "en-US"


def test_invalid_settings_are_reported() -> None:
    with tempfile.TemporaryDirectory(dir=Path.cwd()) as directory:
        settings_path = Path(directory) / "config.json"
        settings_path.write_text("not JSON", encoding="utf-8")

        with pytest.raises(SettingsError, match="Could not read"):
            load_default_language(settings_path)


def test_output_default_is_txt_for_missing_and_legacy_settings(tmp_path: Path) -> None:
    path = tmp_path / "config.json"
    assert load_default_output_format(path) == OutputFormat.TXT
    save_default_language("ar-SA", path)
    assert load_default_output_format(path) == OutputFormat.TXT


def test_settings_updates_preserve_both_preferences(tmp_path: Path) -> None:
    path = tmp_path / "config.json"
    save_default_output_format(OutputFormat.MARKDOWN, path)
    assert load_default_language(path) == "ar"
    save_default_language("de-DE", path)
    assert load_default_output_format(path) == OutputFormat.MARKDOWN
    save_default_output_format(OutputFormat.TXT, path)
    assert load_default_language(path) == "de-DE"


@pytest.mark.parametrize("payload", ["[]", '{"default_output_format": "pdf"}'])
def test_invalid_output_settings_are_reported(tmp_path: Path, payload: str) -> None:
    path = tmp_path / "config.json"
    path.write_text(payload, encoding="utf-8")
    with pytest.raises(SettingsError):
        load_default_output_format(path)
