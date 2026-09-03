"""Right-to-left OCR word ordering."""

from typing import Any


def reconstruct_text(result: Any, rtl: bool) -> str:
    """Reconstruct OCR text line by line from word bounding boxes."""

    lines: list[str] = []

    for line in result.lines:
        words = list(line.words)

        if rtl:
            words.sort(
                key=lambda word: word.bounding_rect.x + word.bounding_rect.width,
                reverse=True,
            )
        else:
            words.sort(key=lambda word: word.bounding_rect.x)

        lines.append(" ".join(word.text for word in words))

    return "\n".join(lines)
