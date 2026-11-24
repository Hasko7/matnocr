"""Synthetic documents and capability checks for real runtime tests."""

import base64
import shutil
import subprocess
import sys
from collections.abc import Callable
from pathlib import Path
from typing import Any

import pytest

SCANNED_TEXT = {
    "de": "Die Schüler lesen Bücher.\nGrüße aus Köln und München.\nDie Straße ist groß.",
    "ar": "هذا كتاب مفيد\nيقرأ الطالب الدرس\nالعلم نور والعمل خير",
}


@pytest.fixture
def pdfium() -> Any:
    return pytest.importorskip("pypdfium2", reason="PDFium is not installed")


@pytest.fixture
def windows_ocr() -> Any:
    if sys.platform != "win32":
        pytest.skip("Windows OCR requires Windows")
    module = pytest.importorskip("winrt.windows.media.ocr")
    try:
        tuple(module.OcrEngine.available_recognizer_languages)
    except (OSError, RuntimeError) as error:
        pytest.skip(f"Windows OCR runtime is unavailable: {error}")
    return module


@pytest.fixture
def english_ocr_language(windows_ocr: Any) -> str:
    languages = windows_ocr.OcrEngine.available_recognizer_languages
    for language in languages:
        if language.language_tag.lower().startswith("en-"):
            return language.language_tag
    pytest.skip("An English Windows OCR language pack is not installed")


@pytest.fixture
def ocr_language(request: pytest.FixtureRequest, windows_ocr: Any) -> str:
    requested = str(request.param)
    for language in windows_ocr.OcrEngine.available_recognizer_languages:
        tag = language.language_tag
        if tag.lower().split("-")[0] == requested:
            return tag
    pytest.skip(f"Windows OCR language pack '{requested}' is not installed")


@pytest.fixture
def scanned_pdf_factory(tmp_path: Path, pdfium: Any) -> Callable[[str], Path]:
    """Render shaped Unicode text and embed it as an image-only PDF."""

    if sys.platform != "win32":
        pytest.skip("Synthetic scan generation uses Windows text rendering")
    powershell = shutil.which("powershell.exe")
    if powershell is None:
        pytest.skip("Windows PowerShell is required to render Unicode test text")

    def create(language: str) -> Path:
        image_path = tmp_path / f"scan-{language}.jpg"
        text = base64.b64encode(SCANNED_TEXT[language].encode("utf-8")).decode("ascii")
        completed = subprocess.run(
            [
                powershell,
                "-NoProfile",
                "-NonInteractive",
                "-File",
                str(Path(__file__).with_name("render_test_text.ps1")),
                "-OutputPath",
                str(image_path),
                "-TextBase64",
                text,
                "-Direction",
                "rtl" if language == "ar" else "ltr",
            ],
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
            creationflags=subprocess.CREATE_NO_WINDOW,
        )
        if completed.returncode == 3:
            pytest.skip(completed.stdout.strip())
        assert completed.returncode == 0, completed.stdout + completed.stderr
        destination = tmp_path / f"scan-{language}.pdf"
        with pdfium.PdfDocument.new() as pdf:
            page = pdf.new_page(400, 200)
            try:
                image = pdfium.PdfImage.new(pdf)
                image.load_jpeg(image_path, inline=True)
                image.set_matrix(pdfium.PdfMatrix(a=400, d=200))
                page.insert_obj(image)
                page.gen_content()
                pdf.save(destination)
            finally:
                page.close()
        return destination

    return create


@pytest.fixture
def synthetic_scanned_pdf(
    ocr_language: str, scanned_pdf_factory: Callable[[str], Path]
) -> Path:
    return scanned_pdf_factory(ocr_language.lower().split("-")[0])


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
