"""MatnOCR application configuration."""

from dataclasses import dataclass
from types import MappingProxyType
from typing import Final

DPI_PRESETS: Final = MappingProxyType(
    {
        "fast": 200,
        "balanced": 250,
        "quality": 300,
    }
)
DPI_CHOICES: Final = (200, 250, 300)
SUPPORTED_DPI: Final = frozenset(DPI_CHOICES)
DEFAULT_DPI: Final = DPI_PRESETS["quality"]
DEFAULT_LANGUAGE: Final = "ar"
MIN_PAGE_COVERAGE: Final = 0.70


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
