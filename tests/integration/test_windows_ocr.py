"""Real OCR smoke test, skipped when the language capability is missing."""

import asyncio
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
