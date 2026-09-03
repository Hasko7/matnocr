"""PDF page selection and range parsing."""

import re
from dataclasses import dataclass

_PAGE_PATTERN = re.compile(r"^[0-9]+$")
_RANGE_PATTERN = re.compile(r"^([0-9]+)-([0-9]+)$")
_EXAMPLE = "Use values such as 1,5,20-35."


class PageRangeError(ValueError):
    """Raised when a user-facing page selection is invalid."""


@dataclass(frozen=True, slots=True)
class _PageSpan:
    first: int
    last: int


def _parse_spans(selection: str) -> list[_PageSpan]:
    value = selection.strip()
    if not value:
        raise PageRangeError(f"Page selection must not be empty. {_EXAMPLE}")

    spans: list[_PageSpan] = []

    for raw_token in value.split(","):
        token = raw_token.strip()
        if not token:
            raise PageRangeError(f"Page selection contains an empty item. {_EXAMPLE}")

        if _PAGE_PATTERN.fullmatch(token):
            page_number = int(token)
            if page_number < 1:
                raise PageRangeError(f"Page numbers start at 1; got {page_number}.")
            spans.append(_PageSpan(page_number, page_number))
            continue

        range_match = _RANGE_PATTERN.fullmatch(token)
        if range_match is None:
            raise PageRangeError(f"Invalid page item '{token}'. {_EXAMPLE}")

        first = int(range_match.group(1))
        last = int(range_match.group(2))

        if first < 1 or last < 1:
            invalid = first if first < 1 else last
            raise PageRangeError(f"Page numbers start at 1; got {invalid}.")
        if first > last:
            raise PageRangeError(f"Page range must be ascending; got {token}.")

        spans.append(_PageSpan(first, last))

    return spans


def validate_page_selection(selection: str) -> None:
    """Validate page-selection syntax without requiring an open PDF."""

    _parse_spans(selection)


def parse_page_range(selection: str, page_count: int) -> list[int]:
    """Convert 1-based user pages to sorted, unique, 0-based PDF indices."""

    if page_count < 0:
        raise ValueError("page_count must not be negative")

    spans = _parse_spans(selection)
    if page_count == 0:
        raise PageRangeError("Cannot select pages from an empty PDF.")

    selected: set[int] = set()

    for span in spans:
        if span.last > page_count:
            raise PageRangeError(
                f"Page {span.last} is outside this PDF; it has {page_count} pages."
            )
        selected.update(range(span.first - 1, span.last))

    return sorted(selected)


def resolve_page_indices(selection: str | None, page_count: int) -> list[int]:
    """Return all PDF indices when no explicit page selection was supplied."""

    if page_count < 0:
        raise ValueError("page_count must not be negative")
    if selection is None:
        return list(range(page_count))
    return parse_page_range(selection, page_count)
