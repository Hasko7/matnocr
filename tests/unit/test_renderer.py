from dataclasses import dataclass

from matnocr.renderer import find_dominant_image


@dataclass
class FakeImage:
    bounds: tuple[float, float, float, float]
    raises: bool = False

    def get_bounds(self) -> tuple[float, float, float, float]:
        if self.raises:
            raise RuntimeError("bad image")
        return self.bounds


@dataclass
class FakePage:
    width: float
    height: float
    images: list[FakeImage]

    def get_width(self) -> float:
        return self.width

    def get_height(self) -> float:
        return self.height

    def get_objects(self, *, filter: list[int]) -> list[FakeImage]:
        assert filter
        return self.images


def test_find_dominant_image_uses_page_coverage() -> None:
    small = FakeImage((0, 0, 2, 2))
    dominant = FakeImage((0, 0, 8, 9))
    broken = FakeImage((0, 0, 10, 10), raises=True)

    image, coverage = find_dominant_image(FakePage(10, 10, [small, broken, dominant]))

    assert image is dominant
    assert coverage == 0.72


def test_find_dominant_image_handles_empty_page() -> None:
    assert find_dominant_image(FakePage(0, 10, [])) == (None, 0.0)
