"""OCR output formatting and writing."""

from collections.abc import Iterable
from pathlib import Path
from tempfile import NamedTemporaryFile

from .config import OutputFormat
from .engine import OcrPageResult, OcrRunResult


def format_page(page_number: int, text: str) -> str:
    """Format one page exactly like the benchmark prototype."""

    return f"\n========== Page {page_number} ==========\n\n{text.strip()}\n"


def format_text_output(pages: Iterable[OcrPageResult]) -> str:
    """Combine page OCR results into the v0.1 TXT representation."""

    return "".join(format_page(page.page_number, page.text) for page in pages)


def format_markdown_output(pages: Iterable[OcrPageResult]) -> str:
    """Separate unmodified OCR page text with Markdown headings."""

    return (
        "\n\n".join(
            f"# Page {page.page_number}\n\n{page.text.strip()}".rstrip()
            for page in pages
        )
        + "\n"
    )


def resolve_output_format(
    output_path: Path | None,
    requested: OutputFormat | None,
    default: OutputFormat = OutputFormat.TXT,
) -> OutputFormat:
    """Prefer a recognized filename extension over the saved default."""

    if output_path is not None and output_path.suffix:
        suffixes = {
            ".txt": OutputFormat.TXT,
            ".md": OutputFormat.MARKDOWN,
            ".markdown": OutputFormat.MARKDOWN,
        }
        inferred = suffixes.get(output_path.suffix.lower())
        if inferred is None:
            raise ValueError("Output extension must be .txt, .md, or .markdown.")
        if requested is not None and requested != inferred:
            raise ValueError("--format conflicts with the output filename extension.")
        return inferred
    return requested or default


def make_output_path(
    pdf_path: Path,
    language_tag: str,
    dpi: int,
    output_format: OutputFormat = OutputFormat.TXT,
) -> Path:
    """Return the default MatnOCR output filename."""

    language_short = language_tag.split("-")[0].lower()
    return pdf_path.with_name(
        f"{pdf_path.stem}_matnocr_{language_short}_{dpi}dpi.{output_format.value}"
    )


def write_text_output(
    result: OcrRunResult,
    output_path: Path | None = None,
    *,
    output_format: OutputFormat = OutputFormat.TXT,
    force: bool = False,
) -> Path:
    """Write raw OCR text as UTF-8 and return the resulting path."""

    destination = resolve_output_path(
        result.pdf_path,
        result.language_tag,
        result.dpi,
        output_path,
        output_format,
    )
    validate_output_path(destination, force=force)
    formatter = (
        format_markdown_output
        if output_format == OutputFormat.MARKDOWN
        else format_text_output
    )
    text = formatter(result.pages)
    if force:
        # Stage the complete text beside the destination so a failed write does
        # not truncate an existing export. Replacement stays on one filesystem.
        temporary_path: Path | None = None
        try:
            with NamedTemporaryFile(
                mode="w",
                encoding="utf-8",
                dir=destination.parent,
                prefix=f".{destination.name}.",
                suffix=".tmp",
                delete=False,
            ) as stream:
                temporary_path = Path(stream.name)
                stream.write(text)
            temporary_path.replace(destination)
        finally:
            if temporary_path is not None:
                temporary_path.unlink(missing_ok=True)
    else:
        # Exclusive creation protects against files appearing after preflight.
        created = False
        try:
            with destination.open("x", encoding="utf-8") as stream:
                created = True
                stream.write(text)
        except OSError:
            if created:
                destination.unlink(missing_ok=True)
            raise
    return destination


def resolve_output_path(
    pdf_path: Path,
    language_tag: str,
    dpi: int,
    output_path: Path | None,
    output_format: OutputFormat,
) -> Path:
    """Resolve the final filename before OCR begins."""

    destination = output_path or make_output_path(
        pdf_path, language_tag, dpi, output_format
    )
    if not destination.suffix:
        destination = destination.with_suffix(f".{output_format.value}")
    return destination


def validate_output_path(destination: Path, *, force: bool = False) -> None:
    """Reject existing targets and invalid parent directories before OCR."""

    if destination.is_dir():
        raise IsADirectoryError(f"Output path is a directory: {destination}")
    if destination.exists() and not force:
        raise FileExistsError(
            f"Output file already exists: {destination}. "
            "Use --force to overwrite it or choose another output path."
        )
    if not destination.parent.exists():
        raise FileNotFoundError(
            f"Output directory does not exist: {destination.parent}"
        )
    if not destination.parent.is_dir():
        raise NotADirectoryError(
            f"Output parent is not a directory: {destination.parent}"
        )
