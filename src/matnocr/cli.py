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
from .language_capabilities import (
    CapabilityAction,
    LanguageCapabilityError,
    get_language_capabilities,
    manage_language_capability,
    normalize_capability_language_tag,
)
from .languages import (
    LanguageNotInstalledError,
    get_available_languages,
    get_language_display_name,
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
    print_error,
    print_language_capabilities_table,
    print_languages_table,
    print_ocr_configuration,
    print_success,
    terminal_supports_color,
)

OCR_EPILOG = """[bold]Examples[/bold]

  matnocr book.pdf
  matnocr ocr book.pdf --pages 1-10 --quality fast
  matnocr book.pdf --lang ar-SA --dpi 300 -o book.txt
"""

LANGUAGES_EPILOG = """[bold]Examples[/bold]

  matnocr languages available
  matnocr languages install fr-FR
  matnocr languages default ar-SA
"""


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

    def format_help(
        self,
        ctx: _click.Context,
        formatter: _click.HelpFormatter,
    ) -> None:
        """Add the current default OCR language to the root help text."""

        original_help = self.help
        original_color = ctx.color
        try:
            ctx.color = terminal_supports_color(sys.stdout)
            default_installed = False
            try:
                configured = load_default_language()
                try:
                    language_tag = resolve_language(configured)
                    language_name = get_language_display_name(language_tag)
                    default_language = f"{language_name} ({language_tag})"
                    default_installed = True
                except LanguageNotInstalledError:
                    language_tag = configured
                    default_language = f"{configured} (not installed)"
            except SettingsError:
                language_tag = ""
                default_language = "unavailable"

            hint = ""
            default_is_arabic = language_tag.lower().split("-")[0] == "ar"
            if default_is_arabic and not default_installed:
                hint = (
                    "\n\nHint: Install Arabic OCR with: matnocr languages install ar-SA"
                )
            elif not default_is_arabic:
                try:
                    resolve_language("ar")
                except LanguageNotInstalledError:
                    hint = (
                        "\n\nHint: Install Arabic OCR with: "
                        "matnocr languages install ar-SA"
                    )

            description = original_help or ""
            self.help = (
                f"{description}\n\nDefault OCR language: {default_language}{hint}"
            )
            super().format_help(ctx, formatter)
        finally:
            self.help = original_help
            ctx.color = original_color


app = typer.Typer(
    cls=DefaultOcrGroup,
    add_completion=False,
    no_args_is_help=True,
    context_settings={"help_option_names": ["-h", "--help"]},
    help=(
        "Fast local OCR for scanned Arabic PDFs, with support for many other languages."
    ),
    rich_markup_mode="rich",
)
languages_app = typer.Typer(
    invoke_without_command=True,
    no_args_is_help=False,
    context_settings={"help_option_names": ["-h", "--help"]},
    epilog=LANGUAGES_EPILOG,
    help="List and manage Windows OCR languages.",
    rich_markup_mode="rich",
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


@app.command("ocr", epilog=OCR_EPILOG)
def main(
    pdf: Annotated[
        Path,
        typer.Argument(
            exists=True,
            file_okay=True,
            dir_okay=False,
            readable=True,
            help="Scanned PDF to recognize.",
            rich_help_panel="Input",
        ),
    ],
    lang: Annotated[
        str | None,
        typer.Option(
            "--lang",
            help="Installed OCR language code, for example ar-SA.",
            metavar="CODE",
            rich_help_panel="Recognition",
        ),
    ] = None,
    dpi: Annotated[
        int | None,
        typer.Option(
            "--dpi",
            help="OCR resolution: 200, 250, or 300 DPI.",
            metavar="DPI",
            rich_help_panel="Recognition",
        ),
    ] = None,
    quality: Annotated[
        QualityPreset | None,
        typer.Option(
            "--quality",
            case_sensitive=False,
            help="Quality preset: fast, balanced, or quality (default).",
            rich_help_panel="Recognition",
        ),
    ] = None,
    pages: Annotated[
        str | None,
        typer.Option(
            "--pages",
            help="Pages to OCR, for example: 1,5,20-35.",
            metavar="RANGE",
            rich_help_panel="Recognition",
        ),
    ] = None,
    output: Annotated[
        Path | None,
        typer.Option(
            "-o",
            "--output",
            dir_okay=False,
            resolve_path=True,
            help="Write OCR text to this file.",
            metavar="FILE",
            rich_help_panel="Output",
        ),
    ] = None,
    quiet: Annotated[
        bool,
        typer.Option(
            "--quiet",
            help="Suppress progress and summary output.",
            rich_help_panel="Output",
        ),
    ] = False,
    no_layout: Annotated[
        bool,
        typer.Option(
            "--no-layout",
            help="Ignore line and paragraph layout; join text continuously.",
            rich_help_panel="Recognition",
        ),
    ] = False,
    show_page_count: Annotated[
        bool,
        typer.Option(
            "--page-count",
            help="Print the PDF page count and exit.",
            rich_help_panel="Output",
        ),
    ] = False,
) -> None:
    """Convert a scanned PDF into text."""

    pdf_path = pdf.resolve()

    if show_page_count:
        if pages is not None:
            raise typer.BadParameter(
                "--page-count cannot be combined with --pages.",
                param_hint="--page-count",
            )
        try:
            page_count = get_pdf_page_count(pdf_path)
        except (OSError, RuntimeError, ValueError) as error:
            print_error(error)
            raise typer.Exit(code=1) from error
        typer.echo(page_count)
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
        print_ocr_configuration(
            pdf_path,
            language_tag,
            resolved_dpi,
            "RTL" if is_rtl(language_tag) else "LTR",
        )

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
    except (OSError, RuntimeError, ValueError) as error:
        print_error(error)
        raise typer.Exit(code=1) from error

    try:
        output_path = write_text_output(result, output)
    except OSError as error:
        print_error(f"Could not write the OCR output: {error}")
        raise typer.Exit(code=1) from error
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
        print_error(error)
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
        print_error(error)
        raise typer.Exit(code=1) from error

    print_success(f"Default OCR language: {language_tag}")
    typer.echo(f"Saved in: {settings_path}")


@languages_app.command("available")
def available_languages_command() -> None:
    """Show every Windows OCR language capability and its installation state."""

    typer.echo(
        "Reading Windows OCR capabilities. Administrator permission may be requested."
    )
    try:
        result = get_language_capabilities()
    except LanguageCapabilityError as error:
        print_error(error)
        raise typer.Exit(code=1) from error

    print_language_capabilities_table(result.capabilities)


def _manage_language_command(action: CapabilityAction, language: str) -> None:
    try:
        language_tag = normalize_capability_language_tag(language)
        if action == "remove":
            default_language = load_default_language().lower()
            requested = language_tag.lower()
            if requested == default_language or requested.startswith(
                default_language + "-"
            ):
                raise LanguageCapabilityError(
                    f"Cannot remove the default OCR language {language_tag}. "
                    "Set another default language first."
                )

        typer.echo(
            "Administrator permission is required. "
            "Approve the Windows UAC prompt to continue."
        )
        result = manage_language_capability(action, language_tag)
    except (LanguageCapabilityError, SettingsError) as error:
        print_error(error)
        raise typer.Exit(code=1) from error

    verb = "installed" if result.action == "install" else "removed"
    print_success(f"OCR language {result.language_tag} {verb}.")
    typer.echo("Run 'matnocr languages' to refresh the installed language list.")


@languages_app.command("install")
def install_language_command(
    language: Annotated[
        str,
        typer.Argument(help="Complete OCR language tag, for example fr-FR."),
    ],
) -> None:
    """Install a Windows OCR language capability with administrator rights."""

    _manage_language_command("install", language)


@languages_app.command("remove")
def remove_language_command(
    language: Annotated[
        str,
        typer.Argument(help="Complete OCR language tag, for example fr-FR."),
    ],
) -> None:
    """Remove a Windows OCR language capability with administrator rights."""

    _manage_language_command("remove", language)


@app.command("doctor")
def doctor_command() -> None:
    """Check the Windows OCR and Direct-RAM runtime environment."""

    checks = run_doctor_checks()
    print_doctor_table(checks)
    if not all(check.passed for check in checks):
        raise typer.Exit(code=1)
