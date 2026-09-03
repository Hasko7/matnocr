import pytest

from matnocr.config import (
    DEFAULT_DPI,
    DEFAULT_QUALITY,
    DPI_CHOICES,
    DPI_PRESETS,
    OcrConfig,
    QualityPreset,
    resolve_dpi,
)


def test_quality_preset_is_the_default() -> None:
    assert DEFAULT_QUALITY is QualityPreset.QUALITY
    assert DEFAULT_DPI == DPI_PRESETS[QualityPreset.QUALITY] == 300
    assert DPI_CHOICES == (200, 250, 300)
    assert OcrConfig().dpi == 300


@pytest.mark.parametrize(
    ("quality", "expected_dpi"),
    [
        (QualityPreset.FAST, 200),
        (QualityPreset.BALANCED, 250),
        (QualityPreset.QUALITY, 300),
    ],
)
def test_quality_presets_resolve_to_dpi(
    quality: QualityPreset,
    expected_dpi: int,
) -> None:
    assert resolve_dpi(None, quality) == expected_dpi


def test_resolve_dpi_defaults_to_quality() -> None:
    assert resolve_dpi(None, None) == 300


def test_direct_dpi_is_supported() -> None:
    assert resolve_dpi(250, None) == 250


def test_dpi_and_quality_conflict_is_rejected() -> None:
    with pytest.raises(ValueError, match="cannot be combined"):
        resolve_dpi(200, QualityPreset.FAST)


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
