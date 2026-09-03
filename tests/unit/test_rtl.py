from dataclasses import dataclass

import pytest

from matnocr.rtl import reconstruct_text


@dataclass
class FakeRect:
    x: float
    width: float
    y: float = 0
    height: float = 10


@dataclass
class FakeWord:
    text: str
    bounding_rect: FakeRect


@dataclass
class FakeLine:
    words: list[FakeWord]


@dataclass
class FakeResult:
    lines: list[FakeLine]


@pytest.fixture
def unordered_result() -> FakeResult:
    return FakeResult(
        lines=[
            FakeLine(
                words=[
                    FakeWord("middle", FakeRect(20, 5)),
                    FakeWord("left", FakeRect(0, 5)),
                    FakeWord("right", FakeRect(40, 5)),
                ]
            ),
            FakeLine(words=[FakeWord("second-line", FakeRect(10, 5))]),
        ]
    )


def test_ltr_words_are_sorted_left_to_right(unordered_result: FakeResult) -> None:
    assert reconstruct_text(unordered_result, rtl=False) == (
        "left middle right\nsecond-line"
    )


def test_rtl_words_are_sorted_right_to_left(unordered_result: FakeResult) -> None:
    assert reconstruct_text(unordered_result, rtl=True) == (
        "right middle left\nsecond-line"
    )


def test_no_layout_joins_all_lines_continuously() -> None:
    result = FakeResult(
        lines=[
            FakeLine(words=[FakeWord("heading", FakeRect(0, 10, 0, 10))]),
            FakeLine(words=[FakeWord("first", FakeRect(0, 10, 35, 10))]),
            FakeLine(words=[FakeWord("second", FakeRect(0, 10, 50, 10))]),
        ]
    )

    assert reconstruct_text(result, rtl=False, preserve_layout=False) == (
        "heading first second"
    )


def test_preserve_layout_adds_blank_line_for_large_vertical_gap() -> None:
    result = FakeResult(
        lines=[
            FakeLine(words=[FakeWord("heading", FakeRect(0, 10, 0, 10))]),
            FakeLine(words=[FakeWord("first", FakeRect(0, 10, 35, 10))]),
            FakeLine(words=[FakeWord("second", FakeRect(0, 10, 50, 10))]),
        ]
    )

    assert reconstruct_text(result, rtl=False) == "heading\n\nfirst\nsecond"


def test_preserve_layout_handles_a_two_line_page() -> None:
    result = FakeResult(
        lines=[
            FakeLine(words=[FakeWord("heading", FakeRect(0, 10, 0, 10))]),
            FakeLine(words=[FakeWord("paragraph", FakeRect(0, 10, 30, 10))]),
        ]
    )

    assert reconstruct_text(result, rtl=False, preserve_layout=True) == (
        "heading\n\nparagraph"
    )


def test_preserve_layout_does_not_mark_uniform_spacing_as_paragraphs() -> None:
    result = FakeResult(
        lines=[
            FakeLine(words=[FakeWord("one", FakeRect(0, 10, 0, 10))]),
            FakeLine(words=[FakeWord("two", FakeRect(0, 10, 25, 10))]),
            FakeLine(words=[FakeWord("three", FakeRect(0, 10, 50, 10))]),
        ]
    )

    assert reconstruct_text(result, rtl=False, preserve_layout=True) == (
        "one\ntwo\nthree"
    )
