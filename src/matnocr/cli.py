"""Typer command-line interface for MatnOCR."""

import asyncio
import sys
from importlib.metadata import version
from pathlib import Path
from typing import Annotated

import typer
from typer import _click
from typer.core import TyperGroup

from .config import QualityPreset, resolve_dpi
from .doctor import run_doctor_checks
from .engine import recognize_pdf
from .languages import (
    LanguageNotInstalledError,
    get_available_languages,
    is_rtl,
    resolve_language,
)
from .output import write_text_output
from .pages import PageRangeError, validate_page_selection
from .renderer import get_pdf_page_count
from .settings import (
    SettingsError,
    load_default_language,
    save_default_language,
)
from .ui import (
    OcrProgress,
    print_completion_summary,
    print_doctor_table,
    print_languages_table,
)


class DefaultOcrGroup(TyperGroup):
    """Route legacy ``matnocr PDF`` invocations to the OCR command."""

    def parse_args(self, ctx: _click.Context, args: list[str]) -> list[str]:
        if (
            args
            and args[0] not in self.commands
            and args[0]
            not in {
                "--help",
                "--version",
            }
        ):
            args.insert(0, "ocr")
        return super().parse_args(ctx, args)


app = typer.Typer(
    cls=DefaultOcrGroup,
    add_completion=False,
    no_args_is_help=True,
    help="Fast local PDF OCR powered by Windows.",
)
languages_app = typer.Typer(
    invoke_without_command=True,
    no_args_is_help=False,
    help="List and manage Windows OCR languages.",
)
app.add_typer(languages_app, name="languages")


def version_callback(value: bool) -> None:
    """Print the installed package version without requiring a PDF argument."""

    if value:
        typer.echo(version("matnocr"))
        raise typer.Exit


def configure_utf8_output() -> None:
    """Allow native language names and status marks on legacy Windows shells."""

    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is not None:
            reconfigure(encoding="utf-8", errors="replace")


@app.callback()
def app_callback(
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
    """Run OCR directly or use a management command."""

    configure_utf8_output()


@app.command("ocr")
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
    lang: Annotated[
        str | None,
        typer.Option("--lang", help="Installed Windows OCR language."),
    ] = None,
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
    no_layout: Annotated[
        bool,
        typer.Option(
            "--no-layout",
            help="Ignore line and paragraph layout; join text continuously.",
        ),
    ] = False,
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

    try:
        requested_language = lang or load_default_language()
        language_tag = resolve_language(requested_language)
    except (LanguageNotInstalledError, SettingsError) as error:
        raise typer.BadParameter(
            str(error),
            param_hint="--lang/default language",
        ) from error

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
        with OcrProgress(enabled=not quiet) as progress:
            result = asyncio.run(
                recognize_pdf(
                    pdf_path,
                    language_tag,
                    resolved_dpi,
                    page_selection=pages,
                    preserve_layout=not no_layout,
                    on_start=None if quiet else progress.begin,
                    on_page=None if quiet else progress.advance,
                )
            )
    except PageRangeError as error:
        raise typer.BadParameter(str(error), param_hint="--pages") from error

    output_path = write_text_output(result, output)
    if not quiet:
        print_completion_summary(result, output_path)


@languages_app.callback()
def languages_command(ctx: typer.Context) -> None:
    """Show all OCR languages currently available to Windows OCR."""

    if ctx.invoked_subcommand is not None:
        return

    try:
        default_language = load_default_language()
    except SettingsError as error:
        typer.echo(f"Error: {error}", err=True)
        raise typer.Exit(code=1) from error

    print_languages_table(get_available_languages(), default_language)


@languages_app.command("default")
def set_default_language_command(
    language: Annotated[
        str,
        typer.Argument(help="Installed OCR language code, for example ar or en-US."),
    ],
) -> None:
    """Set the default language used when --lang is omitted."""

    try:
        language_tag = resolve_language(language)
        settings_path = save_default_language(language_tag)
    except (LanguageNotInstalledError, SettingsError) as error:
        typer.echo(f"✗ {error}", err=True)
        raise typer.Exit(code=1) from error

    typer.echo(f"✓ Default OCR language: {language_tag}")
    typer.echo(f"Saved in: {settings_path}")


@app.command("doctor")
def doctor_command() -> None:
    """Check the Windows OCR and Direct-RAM runtime environment."""

    checks = run_doctor_checks()
    print_doctor_table(checks)
    if not all(check.passed for check in checks):
        raise typer.Exit(code=1)
