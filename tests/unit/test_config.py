import pytest

from matnocr.config import DEFAULT_DPI, DPI_CHOICES, DPI_PRESETS, OcrConfig


def test_quality_preset_is_the_default() -> None:
    assert DEFAULT_DPI == DPI_PRESETS["quality"] == 300
    assert DPI_CHOICES == (200, 250, 300)
    assert OcrConfig().dpi == 300


@pytest.mark.parametrize("dpi", [200, 250, 300])
def test_supported_dpi_values(dpi: int) -> None:
    assert OcrConfig(dpi=dpi).dpi == dpi


def test_unsupported_dpi_is_rejected() -> None:
    with pytest.raises(ValueError, match="Unsupported DPI"):
        OcrConfig(dpi=150)


@pytest.mark.parametrize("coverage", [-0.01, 1.01])
def test_invalid_page_coverage_is_rejected(coverage: float) -> None:
    with pytest.raises(ValueError, match="between 0.0 and 1.0"):
        OcrConfig(min_page_coverage=coverage)
