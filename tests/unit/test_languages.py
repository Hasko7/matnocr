from dataclasses import dataclass
from typing import ClassVar

import pytest

from matnocr import languages


@dataclass
class FakeLanguage:
    language_tag: str
    display_name: str = "Display name"
    native_name: str = "Native name"


class FakeOcrEngine:
    available_recognizer_languages: ClassVar = [
        FakeLanguage("ar-SA"),
        FakeLanguage("de-DE"),
        FakeLanguage("tr"),
    ]


@pytest.fixture(autouse=True)
def fake_ocr_engine(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(languages, "OcrEngine", FakeOcrEngine)


@pytest.mark.parametrize(
    ("requested", "expected"),
    [("ar", "ar-SA"), ("AR-SA", "ar-SA"), ("de", "de-DE"), ("tr", "tr")],
)
def test_resolve_language(requested: str, expected: str) -> None:
    assert languages.resolve_language(requested) == expected


def test_resolve_language_reports_installed_languages() -> None:
    with pytest.raises(
        languages.LanguageNotInstalledError,
        match="Installed languages: ar-SA, de-DE, tr",
    ):
        languages.resolve_language("ru")


@pytest.mark.parametrize("tag", ["ar", "ar-SA", "fa-IR", "ur-PK", "he-IL"])
def test_rtl_languages(tag: str) -> None:
    assert languages.is_rtl(tag)


def test_ltr_language() -> None:
    assert not languages.is_rtl("de-DE")
