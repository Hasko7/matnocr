"""Synthetic documents and capability checks for real runtime tests."""

import sys
from pathlib import Path
from typing import Any

import pytest


@pytest.fixture
def pdfium() -> Any:
    return pytest.importorskip("pypdfium2", reason="PDFium is not installed")


@pytest.fixture
def windows_ocr() -> Any:
    if sys.platform != "win32":
        pytest.skip("Windows OCR requires Windows")
    return pytest.importorskip("winrt.windows.media.ocr")


@pytest.fixture
def english_ocr_language(windows_ocr: Any) -> str:
    languages = windows_ocr.OcrEngine.available_recognizer_languages
    for language in languages:
        if language.language_tag.lower().startswith("en-"):
            return language.language_tag
    pytest.skip("An English Windows OCR language pack is not installed")


@pytest.fixture
def synthetic_pdf(tmp_path: Path) -> Path:
    """Build an original English text PDF without extra dependencies."""

    content = b"BT /F1 24 Tf 30 140 Td (MATNOCR TEST 123) Tj ET"
    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 400 220] "
        b"/Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
        b"<< /Length "
        + str(len(content)).encode()
        + b" >>\nstream\n"
        + content
        + b"\nendstream",
    ]
    data = bytearray(b"%PDF-1.4\n")
    offsets = [0]
    for index, obj in enumerate(objects, start=1):
        offsets.append(len(data))
        data.extend(f"{index} 0 obj\n".encode() + obj + b"\nendobj\n")
    xref = len(data)
    data.extend(f"xref\n0 {len(offsets)}\n0000000000 65535 f \n".encode())
    for offset in offsets[1:]:
        data.extend(f"{offset:010d} 00000 n \n".encode())
    data.extend(
        f"trailer\n<< /Size {len(offsets)} /Root 1 0 R >>\n"
        f"startxref\n{xref}\n%%EOF\n".encode()
    )
    path = tmp_path / "synthetic.pdf"
    path.write_bytes(data)
    return path
