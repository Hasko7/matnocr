"""PDF rendering for the OCR pipeline."""

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal

import pypdfium2 as pdfium
import pypdfium2.raw as pdfium_c
from winrt.windows.graphics.imaging import BitmapPixelFormat, SoftwareBitmap
from winrt.windows.storage.streams import DataWriter

RenderMode = Literal["ORIGINAL", "RENDER"]


@dataclass(frozen=True, slots=True)
class RenderedPage:
    """A page bitmap ready for Windows OCR."""

    bitmap: SoftwareBitmap
    width: int
    height: int
    mode: RenderMode


def get_pdf_page_count(pdf_path: Path) -> int:
    """Return the number of pages in a PDF."""

    with pdfium.PdfDocument(pdf_path) as pdf:
        return len(pdf)


def find_dominant_image(page: Any) -> tuple[Any | None, float]:
    """Return the embedded image covering the largest portion of a PDF page."""

    page_area = page.get_width() * page.get_height()
    if page_area <= 0:
        return None, 0.0

    best_image = None
    best_coverage = 0.0

    for image in page.get_objects(filter=[pdfium_c.FPDF_PAGEOBJ_IMAGE]):
        try:
            left, bottom, right, top = image.get_bounds()
            area = max(0.0, right - left) * max(0.0, top - bottom)
            coverage = area / page_area

            if coverage > best_coverage:
                best_image = image
                best_coverage = coverage
        except Exception:  # noqa: BLE001, S112
            continue

    return best_image, best_coverage


def pdfium_bitmap_to_software_bitmap(
    pdf_bitmap: Any,
) -> tuple[SoftwareBitmap, int, int]:
    """Copy a BGRA PDFium bitmap directly into a Windows SoftwareBitmap."""

    width = pdf_bitmap.width
    height = pdf_bitmap.height

    if pdf_bitmap.mode != "BGRA":
        raise RuntimeError(f"Unsupported PDFium bitmap mode: {pdf_bitmap.mode}")

    row_bytes = width * 4
    raw = bytes(pdf_bitmap.buffer)

    if pdf_bitmap.stride != row_bytes:
        packed = bytearray(row_bytes * height)

        for y in range(height):
            source = y * pdf_bitmap.stride
            destination = y * row_bytes
            packed[destination : destination + row_bytes] = raw[
                source : source + row_bytes
            ]

        raw = bytes(packed)

    writer = DataWriter()

    try:
        writer.write_bytes(raw)
        buffer = writer.detach_buffer()
    finally:
        writer.close()

    software_bitmap = SoftwareBitmap.create_copy_from_buffer(
        buffer,
        BitmapPixelFormat.BGRA8,
        width,
        height,
    )
    return software_bitmap, width, height


def original_image_at_dpi(
    image: Any,
    dpi: int,
) -> tuple[SoftwareBitmap, int, int]:
    """Render an embedded scan image directly at the requested DPI."""

    original_matrix = image.get_matrix()
    scale = dpi / 72.0
    image.set_matrix(original_matrix.scale(scale, scale))

    try:
        pdf_bitmap = image.get_bitmap(render=True, scale_to_original=False)
    finally:
        image.set_matrix(original_matrix)

    try:
        return pdfium_bitmap_to_software_bitmap(pdf_bitmap)
    finally:
        pdf_bitmap.close()


def render_page_at_dpi(
    page: Any,
    dpi: int,
) -> tuple[SoftwareBitmap, int, int]:
    """Render a complete PDF page when the original-scan fast path is unavailable."""

    pdf_bitmap = page.render(
        scale=dpi / 72.0,
        optimize_mode="print",
        no_smoothimage=True,
        force_bitmap_format=pdfium_c.FPDFBitmap_BGRA,
        fill_color=(255, 255, 255, 255),
    )

    try:
        return pdfium_bitmap_to_software_bitmap(pdf_bitmap)
    finally:
        pdf_bitmap.close()


def get_ocr_bitmap(page: Any, dpi: int, min_page_coverage: float) -> RenderedPage:
    """Use the original-scan fast path when possible, otherwise render the page."""

    image, coverage = find_dominant_image(page)
    use_original = image is not None and coverage >= min_page_coverage

    if use_original:
        try:
            bitmap, width, height = original_image_at_dpi(image, dpi)
            return RenderedPage(bitmap, width, height, "ORIGINAL")
        except RuntimeError:
            pass

    bitmap, width, height = render_page_at_dpi(page, dpi)
    return RenderedPage(bitmap, width, height, "RENDER")
