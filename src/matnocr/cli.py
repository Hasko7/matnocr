"""Typer command-line interface for MatnOCR."""

import asyncio
from pathlib import Path
from typing import Annotated

import typer

from .config import DEFAULT_DPI, DEFAULT_LANGUAGE, DPI_CHOICES
from .engine import OcrPageResult, OcrRunResult, recognize_pdf
from .languages import is_rtl, resolve_language
from .output import write_text_output
from .pages import PageRangeError, validate_page_selection
from .renderer import get_pdf_page_count

app = typer.Typer(add_completion=False)


def print_page_progress(page: OcrPageResult) -> None:
    """Print prototype-compatible timing details for one completed page."""

    print(
        f"Page {page.page_number}: {page.timing.total_seconds:.3f}s "
        f"[{page.render_mode}] {page.width}x{page.height} "
        f"[bitmap={page.timing.bitmap_seconds:.3f} "
        f"| OCR={page.timing.ocr_seconds:.3f}]"
    )


def print_summary(result: OcrRunResult, output_path: Path) -> None:
    """Print the same summary fields as the benchmark prototype."""

    page_count = result.page_count
    average_total = result.total_seconds / page_count if page_count else 0.0
    average_bitmap = result.total_bitmap_seconds / page_count if page_count else 0.0
    average_ocr = result.total_ocr_seconds / page_count if page_count else 0.0

    print()
    print("Summary")
    print("-------")
    print(f"Pages:          {page_count}")
    print(f"Original scan:  {result.original_pages}")
    print(f"Rendered:       {result.rendered_pages}")
    print(f"Total:          {result.total_seconds:.3f}s")
    print(f"Average:        {average_total:.3f}s/page")
    print(f"Bitmap:         {average_bitmap:.3f}s/page")
    print(f"OCR:            {average_ocr:.3f}s/page")
    print()
    print(f"Saved: {output_path}")


@app.command()
def main(
    pdf: Annotated[
        Path,
        typer.Argument(
            exists=True,
            file_okay=True,
            dir_okay=False,
            readable=True,
        ),
    ],
    lang: Annotated[str, typer.Option("--lang")] = DEFAULT_LANGUAGE,
    dpi: Annotated[int, typer.Option("--dpi")] = DEFAULT_DPI,
    pages: Annotated[
        str | None,
        typer.Option("--pages", help="Pages to OCR, for example: 1,5,20-35"),
    ] = None,
    show_page_count: Annotated[
        bool,
        typer.Option("--page-count", help="Print the PDF page count and exit."),
    ] = False,
) -> None:
    """Recognize a scanned PDF with Windows OCR."""

    pdf_path = pdf.resolve()

    if show_page_count:
        if pages is not None:
            raise typer.BadParameter(
                "--page-count cannot be combined with --pages.",
                param_hint="--page-count",
            )
        typer.echo(get_pdf_page_count(pdf_path))
        return

    if dpi not in DPI_CHOICES:
        raise typer.BadParameter("DPI must be 200, 250, or 300.", param_hint="--dpi")
    if pages is not None:
        try:
            validate_page_selection(pages)
        except PageRangeError as error:
            raise typer.BadParameter(str(error), param_hint="--pages") from error

    language_tag = resolve_language(lang)

    print()
    print("MatnOCR PDFium DPI test")
    print("-----------------------")
    print(f"PDF:       {pdf_path}")
    print(f"Language:  {language_tag}")
    print(f"DPI:       {dpi}")
    print(f"Direction: {'RTL' if is_rtl(language_tag) else 'LTR'}")
    print("Pipeline:  Direct RAM")
    print()

    try:
        result = asyncio.run(
            recognize_pdf(
                pdf_path,
                language_tag,
                dpi,
                page_selection=pages,
                on_page=print_page_progress,
            )
        )
    except PageRangeError as error:
        raise typer.BadParameter(str(error), param_hint="--pages") from error

    output_path = write_text_output(result)
    print_summary(result, output_path)
