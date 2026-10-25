from dataclasses import dataclass

from matnocr.validation import (
    has_recognized_text,
    is_suspicious_ocr_result,
    validation_result_supports_text,
)


@dataclass
class FakeWord:
    text: str


@dataclass
class FakeLine:
    words: list[FakeWord]


@dataclass
class FakeResult:
    lines: list[FakeLine]


def make_result(lines: list[list[str]]) -> FakeResult:
    return FakeResult(
        lines=[FakeLine([FakeWord(word) for word in line]) for line in lines]
    )


def test_empty_result_has_no_recognized_text() -> None:
    assert not has_recognized_text(make_result([]))
    assert not has_recognized_text(make_result([["  "]]))


def test_result_with_a_word_has_recognized_text() -> None:
    assert has_recognized_text(make_result([["النص"]]))


def test_fragmented_ornament_result_is_suspicious() -> None:
    result = make_result(
        [
            ["سسسسعسسعع"],
            ["fi"],
            ["!"],
            ["٤"],
            ["ا", "و", "خو", "ووه"],
            ["يحمسهم", "هي"],
            ["ه", "و", "خب"],
            [".7"],
            ["ر"],
            ["سبس"],
            ["م"],
            ["أ"],
            ["هسي"],
            ["ه"],
            [".", "سر"],
            ["ر"],
            ["أ)"],
            ["ي"],
            ["٤"],
            ["وواه"],
            ["زأ"],
            ["واو", "وهو", "وه"],
            ["تمير"],
            ["-سسه"],
            ["ب"],
            ["سمى"],
            ["ث"],
            ["مسسسب"],
            ["رأ"],
            ["سس", "سم", "جر"],
            ["إ"],
            ["وو", "او", "وشو", "ا"],
            ["و", "ك", "وو"],
            ["سر"],
            ["و", "و", "كو", "هو", "ههو"],
            ["و", "ا", "و", "اخو"],
            ["ز"],
        ]
    )

    assert is_suspicious_ocr_result(result)


def test_normal_arabic_text_is_not_suspicious() -> None:
    result = make_result(
        [
            ["هذا", "نص", "عربي", "واضح", "للاختبار"],
            ["تحتوي", "الصفحة", "على", "كلمات", "حقيقية"],
            ["ويجب", "الحفاظ", "على", "نتيجة", "التعرف"],
        ]
    )

    assert not is_suspicious_ocr_result(result)


def test_sparse_real_text_does_not_trigger_validation() -> None:
    assert not is_suspicious_ocr_result(make_result([["الفصل", "الأول"]]))


def test_125_dpi_ornament_fragments_do_not_confirm_arabic_text() -> None:
    result = make_result(
        [
            ["«"],
            ["الآ", "<@>", "q@>", "@", "ا", "ا", "اخو"],
            ["<@bq@b", "q@>", "ث", "ث", "<@>"],
            ["@", "ث6", "ث", "ث", "هث", "هث", "اث"],
            ["q@>", "Sىثه", "ث)", "جى", ":ه", "اجها"],
            ["<@>", "هذ٩", "هث", "اث", "هن", "لاثا"],
            ["@", "@", "ه(", "هS", "هث", "<@>", "هث"],
            ["<@b", "q@>", "هث", "هث", "هS", "هث", "ه"],
        ]
    )

    assert not validation_result_supports_text(result, "ar-SA")


def test_normal_125_dpi_arabic_text_confirms_page() -> None:
    result = make_result(
        [
            ["الحمد", "لله", "الذي", "أسس", "قواعد", "الأحكام"],
            ["والصلاة", "والسلام", "على", "رسول", "الإسلام"],
        ]
    )

    assert validation_result_supports_text(result, "ar-SA")
