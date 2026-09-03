import tempfile
from pathlib import Path

import pytest

from matnocr.settings import (
    SettingsError,
    load_default_language,
    save_default_language,
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
