"""Typer command-line interface for MatnOCR."""

import asyncio
from importlib.metadata import version
from pathlib import Path
from typing import Annotated

import typer

from .config import DEFAULT_LANGUAGE, QualityPreset, resolve_dpi
from .engine import OcrPageResult, OcrRunResult, recognize_pdf
from .languages import is_rtl, resolve_language
from .output import write_text_output
from .pages import PageRangeError, validate_page_selection
from .renderer import get_pdf_page_count

app = typer.Typer(add_completion=False)


def version_callback(value: bool) -> None:
    """Print the installed package version without requiring a PDF argument."""

    if value:
        typer.echo(version("matnocr"))
        raise typer.Exit


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
    dpi: Annotated[
        int | None,
        typer.Option("--dpi", help="OCR resolution: 200, 250, or 300 DPI."),
    ] = None,
    quality: Annotated[
        QualityPreset | None,
        typer.Option(
            "--quality",
            case_sensitive=False,
            help="Quality preset: fast, balanced, or quality (default).",
        ),
    ] = None,
    pages: Annotated[
        str | None,
        typer.Option("--pages", help="Pages to OCR, for example: 1,5,20-35"),
    ] = None,
    output: Annotated[
        Path | None,
        typer.Option(
            "-o",
            "--output",
            dir_okay=False,
            resolve_path=True,
            help="Write OCR text to this file.",
        ),
    ] = None,
    quiet: Annotated[
        bool,
        typer.Option("--quiet", help="Suppress progress and summary output."),
    ] = False,
    show_page_count: Annotated[
        bool,
        typer.Option("--page-count", help="Print the PDF page count and exit."),
    ] = False,
    show_version: Annotated[
        bool,
        typer.Option(
            "--version",
            callback=version_callback,
            is_eager=True,
            help="Show the MatnOCR version and exit.",
        ),
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

    try:
        resolved_dpi = resolve_dpi(dpi, quality)
    except ValueError as error:
        raise typer.BadParameter(
            str(error),
            param_hint="--dpi/--quality",
        ) from error

    if pages is not None:
        try:
            validate_page_selection(pages)
        except PageRangeError as error:
            raise typer.BadParameter(str(error), param_hint="--pages") from error

    language_tag = resolve_language(lang)

    if not quiet:
        print()
        print("MatnOCR PDFium DPI test")
        print("-----------------------")
        print(f"PDF:       {pdf_path}")
        print(f"Language:  {language_tag}")
        print(f"DPI:       {resolved_dpi}")
        print(f"Direction: {'RTL' if is_rtl(language_tag) else 'LTR'}")
        print("Pipeline:  Direct RAM")
        print()

    try:
        result = asyncio.run(
            recognize_pdf(
                pdf_path,
                language_tag,
                resolved_dpi,
                page_selection=pages,
                on_page=None if quiet else print_page_progress,
            )
        )
    except PageRangeError as error:
        raise typer.BadParameter(str(error), param_hint="--pages") from error

    output_path = write_text_output(result, output)
    if not quiet:
        print_summary(result, output_path)
