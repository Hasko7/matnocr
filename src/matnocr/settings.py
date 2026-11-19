"""Persistent per-user MatnOCR settings."""

import json
import os
from pathlib import Path
from typing import Final

from .config import DEFAULT_LANGUAGE, OutputFormat

CONFIG_HOME_ENV: Final = "MATNOCR_CONFIG_HOME"


class SettingsError(RuntimeError):
    """Raised when MatnOCR settings cannot be read or written."""


def get_settings_path() -> Path:
    """Return the per-user settings path, with an override for testing."""

    configured_home = os.environ.get(CONFIG_HOME_ENV)
    if configured_home:
        return Path(configured_home).expanduser() / "config.json"

    local_app_data = os.environ.get("LOCALAPPDATA")
    base_path = (
        Path(local_app_data) if local_app_data else Path.home() / "AppData" / "Local"
    )
    return base_path / "MatnOCR" / "config.json"


def _load_settings(path: Path) -> dict[str, object]:
    if not path.exists():
        return {}

    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise SettingsError(f"Could not read MatnOCR settings from {path}.") from error

    if not isinstance(payload, dict):
        raise SettingsError(f"Invalid MatnOCR settings in {path}.")
    return payload


def load_default_language(settings_path: Path | None = None) -> str:
    """Load the configured OCR language, falling back to Arabic."""

    path = settings_path or get_settings_path()
    language_tag = _load_settings(path).get("default_language", DEFAULT_LANGUAGE)
    if not isinstance(language_tag, str) or not language_tag.strip():
        raise SettingsError(f"Invalid default language in MatnOCR settings: {path}.")

    return language_tag


def save_default_language(
    language_tag: str,
    settings_path: Path | None = None,
) -> Path:
    """Persist the default OCR language for the current Windows user."""

    return _save_setting("default_language", language_tag, settings_path)


def load_default_output_format(settings_path: Path | None = None) -> OutputFormat:
    """Load the preferred export format, falling back to TXT."""

    path = settings_path or get_settings_path()
    value = _load_settings(path).get("default_output_format", OutputFormat.TXT)
    try:
        return OutputFormat(value)
    except (TypeError, ValueError) as error:
        raise SettingsError(f"Invalid default output format in {path}.") from error


def save_default_output_format(
    output_format: OutputFormat,
    settings_path: Path | None = None,
) -> Path:
    """Persist the export preference without replacing other settings."""

    return _save_setting(
        "default_output_format", OutputFormat(output_format).value, settings_path
    )


def _save_setting(key: str, value: str, settings_path: Path | None) -> Path:
    path = settings_path or get_settings_path()
    payload = _load_settings(path)
    payload[key] = value
    temporary_path = path.with_suffix(".tmp")

    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        temporary_path.write_text(
            json.dumps(
                payload,
                ensure_ascii=False,
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
        temporary_path.replace(path)
    except OSError as error:
        raise SettingsError(f"Could not write MatnOCR settings to {path}.") from error

    return path
