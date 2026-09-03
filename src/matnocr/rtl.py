"""Right-to-left OCR word ordering."""

from dataclasses import dataclass
from itertools import pairwise
from statistics import median
from typing import Any


@dataclass(frozen=True, slots=True)
class _TextLine:
    text: str
    top: float
    bottom: float
    height: float


def _paragraph_gap_threshold(lines: list[_TextLine]) -> float:
    """Estimate an outlier threshold from this page's line geometry."""

    gaps = [
        max(0.0, following.top - current.bottom)
        for current, following in pairwise(lines)
    ]
    heights = [line.height for line in lines if line.height > 0]

    if not gaps or not heights:
        return float("inf")

    if len(gaps) == 1:
        return median(heights) * 0.8

    ordered_gaps = sorted(gaps)
    baseline_size = max(1, (len(ordered_gaps) + 1) // 2)
    normal_gap = median(ordered_gaps[:baseline_size])

    return max(median(heights) * 0.8, normal_gap * 1.8)


def reconstruct_text(
    result: Any,
    rtl: bool,
    *,
    preserve_layout: bool = True,
) -> str:
    """Reconstruct OCR lines and optionally retain visible paragraph spacing."""

    lines: list[str] = []
    layout_lines: list[_TextLine] = []

    for line in result.lines:
        words = list(line.words)

        if rtl:
            words.sort(
                key=lambda word: word.bounding_rect.x + word.bounding_rect.width,
                reverse=True,
            )
        else:
            words.sort(key=lambda word: word.bounding_rect.x)

        text = " ".join(word.text for word in words)
        lines.append(text)

        if preserve_layout and words:
            top = min(float(word.bounding_rect.y) for word in words)
            bottom = max(
                float(word.bounding_rect.y + word.bounding_rect.height)
                for word in words
            )
            layout_lines.append(
                _TextLine(
                    text=text,
                    top=top,
                    bottom=bottom,
                    height=bottom - top,
                )
            )

    if not preserve_layout:
        return " ".join(line for line in lines if line)

    paragraph_gap = _paragraph_gap_threshold(layout_lines)
    output: list[str] = []

    for index, line in enumerate(layout_lines):
        output.append(line.text)

        if index == len(layout_lines) - 1:
            continue

        gap = max(0.0, layout_lines[index + 1].top - line.bottom)
        if gap > paragraph_gap:
            output.append("")

    return "\n".join(output)
