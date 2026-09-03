"""Windows OCR language discovery and resolution."""

from dataclasses import dataclass
from typing import Final

from winrt.windows.media.ocr import OcrEngine

RTL_LANGUAGES: Final = frozenset({"ar", "fa", "ur", "he"})


@dataclass(frozen=True, slots=True)
class OcrLanguage:
    """Display information for an installed Windows OCR language."""

    language_tag: str
    display_name: str
    native_name: str


class LanguageNotInstalledError(RuntimeError):
    """Raised when Windows OCR does not expose a requested language."""


def get_available_languages() -> tuple[OcrLanguage, ...]:
    """Return the OCR languages currently installed on this Windows device."""

    return tuple(
        OcrLanguage(
            language_tag=language.language_tag,
            display_name=language.display_name,
            native_name=language.native_name,
        )
        for language in OcrEngine.available_recognizer_languages
    )


def resolve_language(requested: str) -> str:
    """Resolve a complete or short language tag against installed OCR languages."""

    requested_normalized = requested.strip().lower()
    languages = get_available_languages()

    for language in languages:
        if language.language_tag.lower() == requested_normalized:
            return language.language_tag

    for language in languages:
        if language.language_tag.lower().startswith(requested_normalized + "-"):
            return language.language_tag

    available = ", ".join(language.language_tag for language in languages) or "none"
    raise LanguageNotInstalledError(
        f"OCR language '{requested}' is not installed. "
        f"Installed languages: {available}. "
        "Install the OCR language through Windows Settings or an elevated "
        "PowerShell, then run 'matnocr languages' again."
    )


def is_rtl(language_tag: str) -> bool:
    """Return whether a Windows language tag uses right-to-left word order."""

    return language_tag.lower().split("-")[0] in RTL_LANGUAGES
