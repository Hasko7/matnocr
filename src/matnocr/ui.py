"""Rich terminal presentation for MatnOCR."""

from collections.abc import Sequence

from rich.console import Console
from rich.table import Table

from .doctor import DiagnosticCheck
from .languages import OcrLanguage


def print_languages_table(
    languages: Sequence[OcrLanguage],
    default_language: str,
    *,
    console: Console | None = None,
) -> None:
    """Display installed Windows OCR languages and the active default."""

    output = console or Console(highlight=False)
    table = Table(title="Installed Windows OCR languages")
    table.add_column("Status")
    table.add_column("Code", style="cyan")
    table.add_column("Name")
    table.add_column("Native name")

    default_normalized = default_language.lower()
    for language in languages:
        tag_normalized = language.language_tag.lower()
        is_default = tag_normalized == default_normalized or tag_normalized.startswith(
            default_normalized + "-"
        )
        status = "✓ Default" if is_default else "✓ Available"
        table.add_row(
            status,
            language.language_tag,
            language.display_name,
            language.native_name,
        )

    output.print(table)
    if not languages:
        output.print("[red]✗ No Windows OCR languages are installed.[/red]")


def print_doctor_table(
    checks: Sequence[DiagnosticCheck],
    *,
    console: Console | None = None,
) -> None:
    """Display MatnOCR diagnostics with clear success and failure markers."""

    output = console or Console(highlight=False)
    table = Table(title="MatnOCR system check")
    table.add_column("Status")
    table.add_column("Check")
    table.add_column("Details")

    for check in checks:
        status = "[green]✓[/green]" if check.passed else "[red]✗[/red]"
        table.add_row(status, check.label, check.details)

    output.print(table)
    if all(check.passed for check in checks):
        output.print("[green]✓ Ready.[/green]")
    else:
        output.print("[red]✗ MatnOCR is not fully ready.[/red]")
