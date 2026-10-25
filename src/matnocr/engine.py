"""Windows OCR engine integration and PDF orchestration."""

import time
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pypdfium2 as pdfium
from winrt.windows.globalization import Language
from winrt.windows.media.ocr import OcrEngine

from .config import MIN_PAGE_COVERAGE, NON_TEXT_VALIDATION_DPI
from .languages import is_rtl
from .pages import resolve_page_indices
from .renderer import RenderMode, get_ocr_bitmap
from .rtl import reconstruct_text
from .validation import is_suspicious_ocr_result, validation_result_supports_text


@dataclass(frozen=True, slots=True)
class PageTiming:
    """Measured durations for one page."""

    bitmap_seconds: float
    ocr_seconds: float
    total_seconds: float


@dataclass(frozen=True, slots=True)
class OcrPageResult:
    """Raw OCR text and timing data for one page."""

    page_number: int
    text: str
    width: int
    height: int
    render_mode: RenderMode
    timing: PageTiming
    skipped_non_text: bool = False


@dataclass(frozen=True, slots=True)
class OcrRunResult:
    """Structured result of a complete PDF OCR run."""

    pdf_path: Path
    language_tag: str
    dpi: int
    pages: tuple[OcrPageResult, ...]
    total_seconds: float
    total_bitmap_seconds: float
    total_ocr_seconds: float
    original_pages: int
    rendered_pages: int
    non_text_validation_pages: int = 0
    skipped_non_text_pages: int = 0

    @property
    def page_count(self) -> int:
        return len(self.pages)


PageCallback = Callable[[OcrPageResult], None]
RunStartCallback = Callable[[int], None]


def create_engine(language_tag: str) -> Any:
    """Create a Windows OCR engine for an installed language tag."""

    engine = OcrEngine.try_create_from_language(Language(language_tag))
    if engine is None:
        raise RuntimeError(f"Could not create Windows OCR engine for {language_tag}")
    return engine


async def recognize(engine: Any, software_bitmap: Any) -> Any:
    """Recognize text in one SoftwareBitmap."""

    return await engine.recognize_async(software_bitmap)


async def recognize_pdf(
    pdf_path: Path,
    language_tag: str,
    dpi: int,
    *,
    page_selection: str | None = None,
    preserve_layout: bool = True,
    min_page_coverage: float = MIN_PAGE_COVERAGE,
    on_start: RunStartCallback | None = None,
    on_page: PageCallback | None = None,
) -> OcrRunResult:
    """Run the unchanged Direct-RAM OCR pipeline for every page in a PDF."""

    engine = create_engine(language_tag)
    rtl = is_rtl(language_tag)
    pages: list[OcrPageResult] = []
    total_bitmap = 0.0
    total_ocr = 0.0
    original_pages = 0
    rendered_pages = 0
    non_text_validation_pages = 0
    skipped_non_text_pages = 0
    total_start = time.perf_counter()

    with pdfium.PdfDocument(pdf_path) as pdf:
        page_indices = resolve_page_indices(page_selection, len(pdf))
        if on_start is not None:
            on_start(len(page_indices))

        for page_index in page_indices:
            page = pdf[page_index]
            page_start = time.perf_counter()

            try:
                bitmap_start = time.perf_counter()
                rendered = get_ocr_bitmap(page, dpi, min_page_coverage)
                bitmap_time = time.perf_counter() - bitmap_start
                total_bitmap += bitmap_time

                if (
                    rendered.width > OcrEngine.max_image_dimension
                    or rendered.height > OcrEngine.max_image_dimension
                ):
                    rendered.bitmap.close()
                    raise RuntimeError(
                        f"Page {page_index + 1}: {rendered.width}x{rendered.height} "
                        f"exceeds Windows OCR limit {OcrEngine.max_image_dimension}"
                    )

                try:
                    ocr_start = time.perf_counter()
                    result = await recognize(engine, rendered.bitmap)
                    ocr_time = time.perf_counter() - ocr_start
                finally:
                    rendered.bitmap.close()

                total_ocr += ocr_time
                skipped_non_text = False

                if is_suspicious_ocr_result(result):
                    non_text_validation_pages += 1
                    validation_bitmap_start = time.perf_counter()
                    validation_rendered = get_ocr_bitmap(
                        page,
                        NON_TEXT_VALIDATION_DPI,
                        min_page_coverage,
                    )
                    validation_bitmap_time = (
                        time.perf_counter() - validation_bitmap_start
                    )
                    bitmap_time += validation_bitmap_time
                    total_bitmap += validation_bitmap_time

                    if (
                        validation_rendered.width > OcrEngine.max_image_dimension
                        or validation_rendered.height > OcrEngine.max_image_dimension
                    ):
                        validation_rendered.bitmap.close()
                        raise RuntimeError(
                            f"Page {page_index + 1}: validation bitmap "
                            f"{validation_rendered.width}x{validation_rendered.height} "
                            f"exceeds Windows OCR limit "
                            f"{OcrEngine.max_image_dimension}"
                        )

                    try:
                        validation_ocr_start = time.perf_counter()
                        validation_result = await recognize(
                            engine,
                            validation_rendered.bitmap,
                        )
                        validation_ocr_time = time.perf_counter() - validation_ocr_start
                    finally:
                        validation_rendered.bitmap.close()

                    ocr_time += validation_ocr_time
                    total_ocr += validation_ocr_time
                    skipped_non_text = not validation_result_supports_text(
                        validation_result,
                        language_tag,
                    )

                if skipped_non_text:
                    text = ""
                    skipped_non_text_pages += 1
                else:
                    text = reconstruct_text(
                        result,
                        rtl,
                        preserve_layout=preserve_layout,
                    )
                page_result = OcrPageResult(
                    page_number=page_index + 1,
                    text=text,
                    width=rendered.width,
                    height=rendered.height,
                    render_mode=rendered.mode,
                    timing=PageTiming(
                        bitmap_seconds=bitmap_time,
                        ocr_seconds=ocr_time,
                        total_seconds=time.perf_counter() - page_start,
                    ),
                    skipped_non_text=skipped_non_text,
                )
                pages.append(page_result)

                if rendered.mode == "ORIGINAL":
                    original_pages += 1
                else:
                    rendered_pages += 1

                if on_page is not None:
                    on_page(page_result)
            finally:
                page.close()

    return OcrRunResult(
        pdf_path=pdf_path,
        language_tag=language_tag,
        dpi=dpi,
        pages=tuple(pages),
        total_seconds=time.perf_counter() - total_start,
        total_bitmap_seconds=total_bitmap,
        total_ocr_seconds=total_ocr,
        original_pages=original_pages,
        rendered_pages=rendered_pages,
        non_text_validation_pages=non_text_validation_pages,
        skipped_non_text_pages=skipped_non_text_pages,
    )
