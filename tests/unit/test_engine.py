import asyncio
from pathlib import Path
from types import SimpleNamespace
from typing import Any, Self

import pytest

from matnocr import engine


class FakePdf:
    def __init__(self, page: Any) -> None:
        self.page = page

    def __enter__(self) -> Self:
        return self

    def __exit__(self, *_exc_info: object) -> None:
        pass

    def __len__(self) -> int:
        return 1

    def __getitem__(self, _index: int) -> Any:
        return self.page


class FakeBitmap:
    def close(self) -> None:
        pass


def make_result(lines: list[list[str]]) -> Any:
    return SimpleNamespace(
        lines=[
            SimpleNamespace(
                words=[
                    SimpleNamespace(
                        text=word,
                        bounding_rect=SimpleNamespace(x=0, y=0, width=1, height=1),
                    )
                    for word in line
                ]
            )
            for line in lines
        ]
    )


def test_suspicious_result_is_rechecked_at_125_dpi(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    page = SimpleNamespace(close=lambda: None)
    rendered_dpis: list[int] = []
    primary_result = make_result([["س"] for _ in range(14)])
    validation_result = make_result([])
    recognition_results = iter((primary_result, validation_result))

    monkeypatch.setattr(engine.pdfium, "PdfDocument", lambda _path: FakePdf(page))
    monkeypatch.setattr(engine, "create_engine", lambda _language: object())
    monkeypatch.setattr(engine, "is_rtl", lambda _language: True)
    monkeypatch.setattr(
        engine,
        "OcrEngine",
        SimpleNamespace(max_image_dimension=10_000),
    )

    def fake_get_ocr_bitmap(_page: Any, dpi: int, _coverage: float) -> Any:
        rendered_dpis.append(dpi)
        return SimpleNamespace(
            bitmap=FakeBitmap(),
            width=100,
            height=200,
            mode="RENDER",
        )

    async def fake_recognize(_ocr_engine: Any, _bitmap: Any) -> Any:
        return next(recognition_results)

    monkeypatch.setattr(engine, "get_ocr_bitmap", fake_get_ocr_bitmap)
    monkeypatch.setattr(engine, "recognize", fake_recognize)

    result = asyncio.run(engine.recognize_pdf(Path("book.pdf"), "ar-SA", 300))

    assert rendered_dpis == [300, 125]
    assert result.non_text_validation_pages == 1
    assert result.skipped_non_text_pages == 1
    assert result.pages[0].skipped_non_text
    assert result.pages[0].text == ""
