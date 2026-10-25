"""Rich terminal presentation for MatnOCR."""

import os
import sys
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import IO, Self

from rich.console import Console
from rich.panel import Panel
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
from rich.theme import Theme

from .doctor import DiagnosticCheck
from .engine import OcrPageResult, OcrRunResult
from .language_capabilities import OcrCapability
from .languages import OcrLanguage

MATNOCR_THEME = Theme(
    {
        "accent": "bold cyan",
        "success": "green",
        "warning": "yellow",
        "error": "bold red",
        "muted": "dim",
    }
)
ACCENT_STYLE = "bold cyan"
SUCCESS_STYLE = "green"
ERROR_STYLE = "bold red"
MUTED_STYLE = "dim"


def terminal_supports_color(
    stream: IO[str],
    *,
    environment: Mapping[str, str] | None = None,
) -> bool:
    """Return whether styled output is appropriate for this terminal."""

    env = os.environ if environment is None else environment
    is_terminal = bool(getattr(stream, "isatty", lambda: False)())
    no_color = "NO_COLOR" in env
    ci = env.get("CI", "").strip().lower() not in {"", "0", "false", "no"}
    dumb_terminal = env.get("TERM", "").lower() == "dumb"
    return is_terminal and not (no_color or ci or dumb_terminal)


def make_console(*, stderr: bool = False) -> Console:
    """Create a consistently styled console that degrades cleanly in CI."""

    stream = sys.stderr if stderr else sys.stdout
    return Console(
        file=stream,
        highlight=False,
        theme=MATNOCR_THEME,
        no_color=not terminal_supports_color(stream),
    )


def print_error(message: object, *, console: Console | None = None) -> None:
    """Print one user-facing error to stderr with a stable format."""

    output = console or make_console(stderr=True)
    line = Text("Error: ", style=ERROR_STYLE)
    line.append(str(message))
    output.print(line, soft_wrap=True)


def print_success(message: object, *, console: Console | None = None) -> None:
    """Print one user-facing success message with a stable format."""

    output = console or make_console()
    line = Text("✓ ", style=SUCCESS_STYLE)
    line.append(str(message))
    output.print(line)


def print_ocr_configuration(
    pdf_path: Path,
    language_tag: str,
    dpi: int,
    direction: str,
    *,
    console: Console | None = None,
) -> None:
    """Display the active OCR settings in a compact panel or plain CI output."""

    output = console or make_console()
    details = Table.grid(padding=(0, 2))
    details.add_column(style=MUTED_STYLE, no_wrap=True)
    details.add_column()
    details.add_row("PDF", str(pdf_path))
    details.add_row("Language", language_tag)
    details.add_row("DPI", str(dpi))
    details.add_row("Direction", direction)
    details.add_row("Pipeline", "Direct RAM")

    if output.is_terminal:
        output.print(Panel(details, title="MatnOCR", border_style=ACCENT_STYLE))
    else:
        output.print("MatnOCR")
        output.print(details)


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
        self.console = console or make_console()
        self.progress = Progress(
            TextColumn(f"[{ACCENT_STYLE}]OCR[/{ACCENT_STYLE}]"),
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

    output = console or make_console()
    pages_per_second = (
        result.page_count / result.total_seconds if result.total_seconds > 0 else 0.0
    )
    page_label = "page" if result.page_count == 1 else "pages"
    output.print(
        f"{result.page_count} {page_label} · "
        f"{result.total_seconds:.1f}s · {pages_per_second:.2f} pages/s"
    )
    print_success(f"Saved to {output_path}", console=output)


def print_languages_table(
    languages: Sequence[OcrLanguage],
    default_language: str,
    *,
    console: Console | None = None,
) -> None:
    """Display installed Windows OCR languages and the active default."""

    output = console or make_console()
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
    table.add_column("Code", style=ACCENT_STYLE)
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
        print_error("No Windows OCR languages are installed.")


def print_language_capabilities_table(
    capabilities: Sequence[OcrCapability],
    *,
    console: Console | None = None,
) -> None:
    """Display all Windows OCR capabilities and their installation state."""

    output = console or make_console()
    table = Table(title="Available Windows OCR language capabilities")
    table.add_column("Code", style=ACCENT_STYLE)
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
        print_error("Windows returned no OCR language capabilities.")
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

    output = console or make_console()
    table = Table(title="MatnOCR system check")
    table.add_column("Status")
    table.add_column("Check")
    table.add_column("Details")

    for check in checks:
        status = "[green]✓[/green]" if check.passed else "[bold red]✗[/bold red]"
        table.add_row(status, check.label, check.details)

    output.print(table)
    if all(check.passed for check in checks):
        print_success("Ready.", console=output)
    else:
        print_error("MatnOCR is not fully ready.")
