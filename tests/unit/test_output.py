from pathlib import Path
from typing import Any

import pytest

from matnocr.config import OutputFormat
from matnocr.engine import OcrPageResult, OcrRunResult, PageTiming
from matnocr.output import (
    format_markdown_output,
    format_page,
    format_text_output,
    make_output_path,
    resolve_output_format,
    validate_output_path,
    write_text_output,
)


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


def test_markdown_preserves_page_numbers_arabic_and_spacing() -> None:
    assert (
        format_markdown_output(
            [
                make_page(9, "نص عربي\nسطر آخر\n\nفقرة"),
                make_page(10, ""),
                make_page(12, "*raw* text"),
            ]
        )
        == "# Page 9\n\nنص عربي\nسطر آخر\n\nفقرة\n\n# Page 10\n\n# Page 12\n\n*raw* text\n"
    )


@pytest.mark.parametrize("suffix", [".md", ".MD", ".markdown"])
def test_markdown_extension_overrides_txt_default(suffix: str) -> None:
    assert resolve_output_format(Path("book" + suffix), None) == OutputFormat.MARKDOWN


def test_txt_extension_overrides_markdown_default() -> None:
    assert (
        resolve_output_format(Path("book.txt"), None, OutputFormat.MARKDOWN)
        == OutputFormat.TXT
    )


def test_unknown_extension_and_explicit_format_conflict_are_rejected() -> None:
    with pytest.raises(ValueError, match="extension"):
        resolve_output_format(Path("book.pdf"), None)
    with pytest.raises(ValueError, match="conflicts"):
        resolve_output_format(Path("book.md"), OutputFormat.TXT)


def test_markdown_default_filename() -> None:
    assert make_output_path(
        Path("book.pdf"), "ar-SA", 300, OutputFormat.MARKDOWN
    ) == Path("book_matnocr_ar_300dpi.md")


def make_run(source: Path) -> OcrRunResult:
    return OcrRunResult(source, "ar-SA", 300, (make_page(9, "نص عربي"),), 0, 0, 0, 1, 0)


@pytest.mark.parametrize("output_format", list(OutputFormat))
def test_existing_exports_require_force(
    tmp_path: Path, output_format: OutputFormat
) -> None:
    run = make_run(tmp_path / "book.pdf")
    path = make_output_path(run.pdf_path, "ar-SA", 300, output_format)
    path.write_text("original", encoding="utf-8")
    with pytest.raises(FileExistsError, match="--force"):
        write_text_output(run, output_format=output_format)
    assert path.read_text(encoding="utf-8") == "original"
    assert write_text_output(run, output_format=output_format, force=True) == path
    assert "نص عربي" in path.read_text(encoding="utf-8")
    assert not list(tmp_path.glob("*.tmp"))


def test_exclusive_creation_handles_a_file_appearing_after_preflight(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from matnocr import output

    path = tmp_path / "out.txt"

    def concurrent_file(_path: Path, *, force: bool) -> None:
        path.write_text("another writer", encoding="utf-8")

    monkeypatch.setattr(output, "validate_output_path", concurrent_file)
    with pytest.raises(FileExistsError):
        write_text_output(make_run(tmp_path / "book.pdf"), path)
    assert path.read_text(encoding="utf-8") == "another writer"


def test_force_replace_failure_preserves_old_export_and_cleans_temp(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    path = tmp_path / "out.txt"
    path.write_text("original", encoding="utf-8")

    def denied(_self: Path, _target: Path) -> Path:
        raise PermissionError("file is locked")

    monkeypatch.setattr(Path, "replace", denied)
    with pytest.raises(PermissionError, match="file is locked"):
        write_text_output(make_run(tmp_path / "book.pdf"), path, force=True)
    assert path.read_text(encoding="utf-8") == "original"
    assert sorted(p.name for p in tmp_path.iterdir()) == ["out.txt"]


def test_unwritable_output_is_reported_without_creating_file(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    path = tmp_path / "out.txt"

    def denied(*_args: object, **_kwargs: object) -> None:
        raise PermissionError("access denied")

    monkeypatch.setattr(Path, "open", denied)
    with pytest.raises(PermissionError, match="access denied"):
        write_text_output(make_run(tmp_path / "book.pdf"), path)
    assert not path.exists()


def test_output_directory_and_file_parent_are_rejected(tmp_path: Path) -> None:
    with pytest.raises(IsADirectoryError):
        validate_output_path(tmp_path, force=True)
    parent_file = tmp_path / "parent"
    parent_file.touch()
    with pytest.raises(NotADirectoryError):
        validate_output_path(parent_file / "out.txt")


@pytest.mark.parametrize("force", [False, True])
def test_partial_write_failure_preserves_existing_data(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, force: bool
) -> None:
    from matnocr import output

    path = tmp_path / "out.txt"
    if force:
        path.write_text("original", encoding="utf-8")

    class FailingWriter:
        def __init__(self, stream: Any) -> None:
            self.stream = stream
            self.name = stream.name

        def __enter__(self) -> Any:
            return self

        def __exit__(self, *exc: Any) -> None:
            self.stream.__exit__(*exc)

        def write(self, text: str) -> int:
            self.stream.write(text[:5])
            raise OSError("disk full")

    with monkeypatch.context() as patch:
        if force:
            original_temp = output.NamedTemporaryFile

            def failing_temp(*args: Any, **kwargs: Any) -> Any:
                return FailingWriter(original_temp(*args, **kwargs))

            patch.setattr(output, "NamedTemporaryFile", failing_temp)
        else:
            original_open = Path.open

            def failing_open(self: Path, *args: Any, **kwargs: Any) -> Any:
                return FailingWriter(original_open(self, *args, **kwargs))

            patch.setattr(Path, "open", failing_open)
        with pytest.raises(OSError, match="disk full"):
            write_text_output(make_run(tmp_path / "book.pdf"), path, force=force)

    if force:
        assert path.read_text(encoding="utf-8") == "original"
    else:
        assert not path.exists()
    assert not list(tmp_path.glob("*.tmp"))
