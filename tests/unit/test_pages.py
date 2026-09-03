import pytest

from matnocr.pages import (
    PageRangeError,
    parse_page_range,
    resolve_page_indices,
    validate_page_selection,
)


@pytest.mark.parametrize(
    ("selection", "expected"),
    [
        ("1", [0]),
        ("1-10", list(range(10))),
        ("1,5,10", [0, 4, 9]),
        ("1,5,20-35,100", [0, 4, *range(19, 35), 99]),
    ],
)
def test_supported_page_selections(selection: str, expected: list[int]) -> None:
    assert parse_page_range(selection, page_count=100) == expected


def test_duplicates_are_removed_and_pages_are_sorted() -> None:
    assert parse_page_range("3,1,2,2,1-3", page_count=3) == [0, 1, 2]


def test_whitespace_around_items_is_accepted() -> None:
    assert parse_page_range(" 1, 5, 20-22 ", page_count=22) == [0, 4, 19, 20, 21]


@pytest.mark.parametrize(
    ("selection", "message"),
    [
        ("0", "Page numbers start at 1"),
        ("-3", "Invalid page item '-3'"),
        ("8-3", "Page range must be ascending"),
        ("abc", "Invalid page item 'abc'"),
        ("1,,2", "contains an empty item"),
        ("1-2-3", "Invalid page item '1-2-3'"),
        ("", "must not be empty"),
    ],
)
def test_invalid_page_selections(selection: str, message: str) -> None:
    with pytest.raises(PageRangeError, match=message):
        validate_page_selection(selection)


def test_page_outside_pdf_is_rejected_before_range_expansion() -> None:
    with pytest.raises(PageRangeError, match="Page 500.*300 pages"):
        parse_page_range("1-500", page_count=300)


def test_explicit_selection_from_empty_pdf_is_rejected() -> None:
    with pytest.raises(PageRangeError, match="empty PDF"):
        parse_page_range("1", page_count=0)


def test_no_selection_returns_every_page() -> None:
    assert resolve_page_indices(None, page_count=4) == [0, 1, 2, 3]
