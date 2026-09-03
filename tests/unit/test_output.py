from pathlib import Path

from matnocr.engine import OcrPageResult, PageTiming
from matnocr.output import format_page, format_text_output, make_output_path


def make_page(page_number: int, text: str) -> OcrPageResult:
    return OcrPageResult(
        page_number=page_number,
        text=text,
        width=100,
        height=200,
        render_mode="ORIGINAL",
        timing=PageTiming(0.1, 0.2, 0.3),
    )


def test_format_page_matches_prototype_markers() -> None:
    assert format_page(2, "  raw OCR  \n") == (
        "\n========== Page 2 ==========\n\nraw OCR\n"
    )


def test_format_text_output_preserves_page_order() -> None:
    assert format_text_output([make_page(1, "one"), make_page(2, "two")]) == (
        "\n========== Page 1 ==========\n\none\n\n========== Page 2 ==========\n\ntwo\n"
    )


def test_default_output_path_uses_matnocr_name() -> None:
    assert make_output_path(Path("book.pdf"), "ar-SA", 300) == Path(
        "book_matnocr_ar_300dpi.txt"
    )
