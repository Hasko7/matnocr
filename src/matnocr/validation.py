"""Conservative detection of suspicious Windows OCR results."""

from typing import Any

MIN_SUSPICIOUS_WORDS = 12
MAX_SHORT_WORD_LENGTH = 2
MAX_SHORT_LINE_LENGTH = 3
MIN_SHORT_WORD_RATIO = 0.65
MIN_SHORT_LINE_RATIO = 0.55
MAX_LONG_WORD_RATIO = 0.10
MIN_LONG_WORD_LENGTH = 4
MAX_INCOMPATIBLE_TOKEN_RATIO = 0.20
ARABIC_SCRIPT_LANGUAGES = frozenset({"ar", "fa", "ur"})
COMMON_PUNCTUATION = frozenset(".,;:!?()[]{}'\"«»-–—…/%،؛؟")


def _content_length(text: str) -> int:
    """Count letters and numbers while ignoring punctuation and whitespace."""

    return sum(character.isalnum() for character in text)


def has_recognized_text(result: Any) -> bool:
    """Return whether an OCR result contains any non-whitespace word."""

    return any(str(word.text).strip() for line in result.lines for word in line.words)


def _words(result: Any) -> list[str]:
    return [
        str(word.text).strip()
        for line in result.lines
        for word in line.words
        if str(word.text).strip()
    ]


def _is_arabic_script_character(character: str) -> bool:
    codepoint = ord(character)
    return (
        0x0600 <= codepoint <= 0x06FF
        or 0x0750 <= codepoint <= 0x077F
        or 0x08A0 <= codepoint <= 0x08FF
        or 0xFB50 <= codepoint <= 0xFDFF
        or 0xFE70 <= codepoint <= 0xFEFF
    )


def _is_arabic_validation_token(token: str) -> bool:
    return all(
        _is_arabic_script_character(character)
        or character.isdigit()
        or character.isspace()
        or character in COMMON_PUNCTUATION
        for character in token
    )


def validation_result_supports_text(result: Any, language_tag: str) -> bool:
    """Return whether a low-resolution result credibly confirms real text."""

    words = _words(result)
    if not words or is_suspicious_ocr_result(result):
        return False

    language = language_tag.split("-", maxsplit=1)[0].lower()
    if language not in ARABIC_SCRIPT_LANGUAGES:
        return True

    incompatible_ratio = sum(
        not _is_arabic_validation_token(word) for word in words
    ) / len(words)
    return incompatible_ratio <= MAX_INCOMPATIBLE_TOKEN_RATIO


def is_suspicious_ocr_result(result: Any) -> bool:
    """Identify fragmented OCR typical of ornaments mistaken for text.

    This intentionally requires several simultaneous warning signs so that short
    headings, page numbers, poetry, and other sparse real text are not retried.
    """

    words = _words(result)
    if len(words) < MIN_SUSPICIOUS_WORDS:
        return False

    word_lengths = [_content_length(word) for word in words]
    short_word_ratio = sum(
        length <= MAX_SHORT_WORD_LENGTH for length in word_lengths
    ) / len(word_lengths)
    long_word_ratio = sum(
        length >= MIN_LONG_WORD_LENGTH for length in word_lengths
    ) / len(word_lengths)

    line_lengths = [
        sum(_content_length(str(word.text)) for word in line.words)
        for line in result.lines
        if any(str(word.text).strip() for word in line.words)
    ]
    short_line_ratio = sum(
        length <= MAX_SHORT_LINE_LENGTH for length in line_lengths
    ) / len(line_lengths)

    return (
        short_word_ratio >= MIN_SHORT_WORD_RATIO
        and short_line_ratio >= MIN_SHORT_LINE_RATIO
        and long_word_ratio <= MAX_LONG_WORD_RATIO
    )
