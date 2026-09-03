from dataclasses import dataclass

import pytest

from matnocr.rtl import reconstruct_text


@dataclass
class FakeRect:
    x: float
    width: float


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
