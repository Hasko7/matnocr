from io import StringIO
from pathlib import Path

from rich.console import Console

from matnocr.engine import OcrPageResult, OcrRunResult, PageTiming
from matnocr.ui import OcrProgress, print_completion_summary


def make_page(page_number: int) -> OcrPageResult:
    return OcrPageResult(
        page_number=page_number,
        text="text",
        width=100,
        height=200,
        render_mode="ORIGINAL",
        timing=PageTiming(0.1, 0.2, 0.3),
    )


def test_progress_shows_page_count_page_number_speed_and_time() -> None:
    stream = StringIO()
    console = Console(
        file=stream,
        force_terminal=True,
        color_system=None,
        width=140,
    )

    with OcrProgress(console=console) as progress:
        progress.begin(2)
        progress.advance(make_page(4))
        progress.advance(make_page(9))

    rendered = stream.getvalue()
    assert "OCR" in rendered
    assert "2/2" in rendered
    assert "page 9" in rendered
    assert "pages/s" in rendered
    assert "elapsed" in rendered
    assert "ETA" in rendered


def test_completion_summary_shows_throughput_and_output_path() -> None:
    stream = StringIO()
    console = Console(file=stream, force_terminal=False, color_system=None)
    pages = (make_page(1), make_page(2))
    result = OcrRunResult(
        pdf_path=Path("book.pdf"),
        language_tag="en-US",
        dpi=300,
        pages=pages,
        total_seconds=2.0,
        total_bitmap_seconds=0.2,
        total_ocr_seconds=1.5,
        original_pages=2,
        rendered_pages=0,
    )

    print_completion_summary(result, Path("output.txt"), console=console)

    assert stream.getvalue() == (
        "2 pages · 2.0s · 1.00 pages/s\n✓ Saved to output.txt\n"
    )
