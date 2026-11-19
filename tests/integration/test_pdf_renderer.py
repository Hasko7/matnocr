"""Exercise the real renderer and bitmap copy with synthetic input."""

from collections.abc import Callable
from pathlib import Path
from typing import Any

import pytest

pytestmark = pytest.mark.integration


@pytest.mark.parametrize("language", ["de", "ar"])
def test_unicode_test_pdf_contains_a_scan_without_hidden_text(
    pdfium: Any, scanned_pdf_factory: Callable[[str], Path], language: str
) -> None:
    with pdfium.PdfDocument(scanned_pdf_factory(language)) as pdf:
        assert len(pdf) == 1
        page = pdf[0]
        try:
            textpage = page.get_textpage()
            try:
                assert textpage.count_chars() == 0
            finally:
                textpage.close()
            objects = list(page.get_objects())
            assert len(objects) == 1
            assert objects[0].get_px_size() == (1600, 800)
        finally:
            page.close()


def test_synthetic_pdf_renders(pdfium: Any, synthetic_pdf: Path) -> None:
    with pdfium.PdfDocument(synthetic_pdf) as pdf:
        assert len(pdf) == 1
        page = pdf[0]
        try:
            bitmap = page.render(scale=2)
            try:
                assert (bitmap.width, bitmap.height) == (800, 440)
                assert len(bytes(bitmap.buffer)) >= 800 * 440 * 3
            finally:
                bitmap.close()
        finally:
            page.close()


def test_direct_ram_bitmap_survives_pdfium_close(
    pdfium: Any, windows_ocr: Any, synthetic_pdf: Path
) -> None:
    from matnocr.renderer import render_page_at_dpi

    with pdfium.PdfDocument(synthetic_pdf) as pdf:
        page = pdf[0]
        try:
            bitmap, width, height = render_page_at_dpi(page, 200)
        finally:
            page.close()
    try:
        # PDFium document and source bitmap are already closed.
        assert bitmap.pixel_width == width
        assert bitmap.pixel_height == height
        from winrt.windows.storage.streams import Buffer

        buffer = Buffer(width * height * 4)
        bitmap.copy_to_buffer(buffer)
        assert buffer.length == width * height * 4
    finally:
        bitmap.close()
