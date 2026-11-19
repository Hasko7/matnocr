"""Real OCR smoke test, skipped when the language capability is missing."""

import asyncio
import re
from pathlib import Path

import pytest

pytestmark = pytest.mark.integration


def test_synthetic_document_is_recognized(
    english_ocr_language: str, synthetic_pdf: Path
) -> None:
    from matnocr.engine import recognize_pdf

    result = asyncio.run(recognize_pdf(synthetic_pdf, english_ocr_language, 200))
    assert result.page_count == 1
    assert result.pages[0].render_mode == "RENDER"
    assert "MATNOCR" in result.pages[0].text.upper()
    assert "123" in result.pages[0].text


@pytest.mark.parametrize("ocr_language", ["de", "ar"], indirect=True)
def test_unicode_scan_recognition_and_word_order(
    ocr_language: str, synthetic_scanned_pdf: Path
) -> None:
    from matnocr.engine import recognize_pdf

    result = asyncio.run(recognize_pdf(synthetic_scanned_pdf, ocr_language, 300))
    assert result.page_count == 1
    page = result.pages[0]
    assert page.render_mode == "ORIGINAL"
    assert not page.skipped_non_text
    words = re.findall(r"\w+", page.text.lower())
    # Anchor words exercise umlauts/eszett and connected Arabic/RTL without
    # requiring identical punctuation or every OCR character on every OS build.
    anchors = (
        ["schüler", "bücher", "grüße", "straße"]
        if ocr_language.lower().startswith("de")
        else ["هذا", "كتاب", "مفيد", "الطالب", "الدرس", "العلم", "نور", "خير"]
    )
    for word in anchors:
        assert word in words, page.text
    positions = [words.index(word) for word in anchors]
    assert positions == sorted(positions), page.text
