"""Windows OCR language discovery and resolution."""

from typing import Final

from winrt.windows.media.ocr import OcrEngine

RTL_LANGUAGES: Final = frozenset({"ar", "fa", "ur", "he"})


def resolve_language(requested: str) -> str:
    """Resolve a complete or short language tag against installed OCR languages."""

    requested = requested.lower()
    languages = list(OcrEngine.available_recognizer_languages)

    for language in languages:
        if language.language_tag.lower() == requested:
            return language.language_tag

    for language in languages:
        if language.language_tag.lower().startswith(requested + "-"):
            return language.language_tag

    available = ", ".join(language.language_tag for language in languages)
    raise RuntimeError(
        f"OCR language '{requested}' is not installed. Installed: {available}"
    )


def is_rtl(language_tag: str) -> bool:
    """Return whether a Windows language tag uses right-to-left word order."""

    return language_tag.lower().split("-")[0] in RTL_LANGUAGES
