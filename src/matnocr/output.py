"""OCR output formatting and writing."""

from collections.abc import Iterable
from pathlib import Path

from .engine import OcrPageResult, OcrRunResult


def format_page(page_number: int, text: str) -> str:
    """Format one page exactly like the benchmark prototype."""

    return f"\n========== Page {page_number} ==========\n\n{text.strip()}\n"


def format_text_output(pages: Iterable[OcrPageResult]) -> str:
    """Combine page OCR results into the v0.1 TXT representation."""

    return "".join(format_page(page.page_number, page.text) for page in pages)


def make_output_path(pdf_path: Path, language_tag: str, dpi: int) -> Path:
    """Return the default MatnOCR output filename."""

    language_short = language_tag.split("-")[0].lower()
    return pdf_path.with_name(f"{pdf_path.stem}_matnocr_{language_short}_{dpi}dpi.txt")


def write_text_output(result: OcrRunResult, output_path: Path | None = None) -> Path:
    """Write raw OCR text as UTF-8 and return the resulting path."""

    destination = output_path or make_output_path(
        result.pdf_path,
        result.language_tag,
        result.dpi,
    )
    destination.write_text(format_text_output(result.pages), encoding="utf-8")
    return destination
