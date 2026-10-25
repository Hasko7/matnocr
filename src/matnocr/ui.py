"""Rich terminal presentation for MatnOCR."""

from collections.abc import Sequence
from pathlib import Path
from typing import Self

from rich.console import Console
from rich.progress import (
    BarColumn,
    MofNCompleteColumn,
    Progress,
    ProgressColumn,
    Task,
    TaskID,
    TextColumn,
    TimeElapsedColumn,
    TimeRemainingColumn,
)
from rich.table import Table
from rich.text import Text

from .doctor import DiagnosticCheck
from .engine import OcrPageResult, OcrRunResult
from .language_capabilities import OcrCapability
from .languages import OcrLanguage


class PagesPerSecondColumn(ProgressColumn):
    """Render OCR throughput without byte-oriented Rich formatting."""

    def render(self, task: Task) -> Text:
        speed = task.finished_speed or task.speed
        value = "?" if speed is None else f"{speed:.2f}"
        return Text(f"{value} pages/s", style="progress.data.speed")


class OcrProgress:
    """Lifecycle-safe Rich progress display for one OCR run."""

    def __init__(
        self,
        *,
        enabled: bool = True,
        console: Console | None = None,
    ) -> None:
        self.console = console or Console(highlight=False)
        self.progress = Progress(
            TextColumn("[bold cyan]OCR[/bold cyan]"),
            BarColumn(bar_width=None),
            MofNCompleteColumn(),
            TextColumn("· page {task.fields[page_number]}"),
            PagesPerSecondColumn(),
            TextColumn("· elapsed"),
            TimeElapsedColumn(),
            TextColumn("· ETA"),
            TimeRemainingColumn(compact=True),
            console=self.console,
            disable=not enabled or not self.console.is_terminal,
            transient=False,
        )
        self.task_id: TaskID | None = None

    def __enter__(self) -> Self:
        self.progress.start()
        return self

    def __exit__(self, *_exc_info: object) -> None:
        self.progress.stop()

    def begin(self, total_pages: int) -> None:
        """Initialize the task once the engine knows the selected page count."""

        self.task_id = self.progress.add_task(
            "OCR",
            total=total_pages,
            page_number="-",
        )

    def advance(self, page: OcrPageResult) -> None:
        """Advance the display after one PDF page has completed."""

        if self.task_id is None:
            raise RuntimeError("OCR progress was advanced before it was initialized.")
        self.progress.update(
            self.task_id,
            advance=1,
            page_number=page.page_number,
        )


def print_completion_summary(
    result: OcrRunResult,
    output_path: Path,
    *,
    console: Console | None = None,
) -> None:
    """Display the concise final OCR timing and destination summary."""

    output = console or Console(highlight=False)
    pages_per_second = (
        result.page_count / result.total_seconds if result.total_seconds > 0 else 0.0
    )
    page_label = "page" if result.page_count == 1 else "pages"
    output.print(
        f"{result.page_count} {page_label} · "
        f"{result.total_seconds:.1f}s · {pages_per_second:.2f} pages/s"
    )
    output.print("[green]✓[/green] Saved to", output_path)


def print_languages_table(
    languages: Sequence[OcrLanguage],
    default_language: str,
    *,
    console: Console | None = None,
) -> None:
    """Display installed Windows OCR languages and the active default."""

    output = console or Console(highlight=False)
    default_normalized = default_language.lower()
    default_display = next(
        (
            language.language_tag
            for language in languages
            if language.language_tag.lower() == default_normalized
            or language.language_tag.lower().startswith(default_normalized + "-")
        ),
        f"{default_language} (not installed)",
    )
    output.print("Default OCR language:", default_display)
    table = Table(title="Installed Windows OCR languages")
    table.add_column("Status")
    table.add_column("Code", style="cyan")
    table.add_column("Name")
    table.add_column("Native name")

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


def print_language_capabilities_table(
    capabilities: Sequence[OcrCapability],
    *,
    console: Console | None = None,
) -> None:
    """Display all Windows OCR capabilities and their installation state."""

    output = console or Console(highlight=False)
    table = Table(title="Available Windows OCR language capabilities")
    table.add_column("Code", style="cyan")
    table.add_column("Language")
    table.add_column("Status")

    for capability in capabilities:
        installed = capability.state.lower() == "installed"
        status = "[green]✓ Installed[/green]" if installed else "Not installed"
        table.add_row(
            capability.language_tag,
            capability.display_name or capability.language_tag,
            status,
        )

    output.print(table)
    if not capabilities:
        output.print("[red]✗ Windows returned no OCR language capabilities.[/red]")
    else:
        output.print(
            "[dim]Hint: Use a code above: matnocr languages install <code>[/dim]"
        )


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
