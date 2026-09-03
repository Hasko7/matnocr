"""MatnOCR application configuration."""

from dataclasses import dataclass
from enum import StrEnum
from types import MappingProxyType
from typing import Final


class QualityPreset(StrEnum):
    """Named OCR quality levels exposed by the CLI."""

    FAST = "fast"
    BALANCED = "balanced"
    QUALITY = "quality"


DPI_PRESETS: Final = MappingProxyType(
    {
        QualityPreset.FAST: 200,
        QualityPreset.BALANCED: 250,
        QualityPreset.QUALITY: 300,
    }
)
DPI_CHOICES: Final = (200, 250, 300)
SUPPORTED_DPI: Final = frozenset(DPI_CHOICES)
DEFAULT_QUALITY: Final = QualityPreset.QUALITY
DEFAULT_DPI: Final = DPI_PRESETS[DEFAULT_QUALITY]
DEFAULT_LANGUAGE: Final = "ar"
MIN_PAGE_COVERAGE: Final = 0.70


def resolve_dpi(dpi: int | None, quality: QualityPreset | None) -> int:
    """Resolve a direct DPI or quality preset to a supported DPI value."""

    if dpi is not None and quality is not None:
        raise ValueError("--dpi and --quality cannot be combined.")

    if dpi is not None:
        if dpi not in SUPPORTED_DPI:
            raise ValueError("DPI must be 200, 250, or 300.")
        return dpi

    return DPI_PRESETS[quality or DEFAULT_QUALITY]


@dataclass(frozen=True, slots=True)
class OcrConfig:
    """Validated settings for a single OCR run."""

    language: str = DEFAULT_LANGUAGE
    dpi: int = DEFAULT_DPI
    min_page_coverage: float = MIN_PAGE_COVERAGE

    def __post_init__(self) -> None:
        if self.dpi not in SUPPORTED_DPI:
            supported = ", ".join(str(value) for value in sorted(SUPPORTED_DPI))
            raise ValueError(
                f"Unsupported DPI {self.dpi}. Expected one of: {supported}"
            )

        if not 0.0 <= self.min_page_coverage <= 1.0:
            raise ValueError("min_page_coverage must be between 0.0 and 1.0")
