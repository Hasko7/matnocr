"""Runtime diagnostics for MatnOCR."""

import platform
import sys
from dataclasses import dataclass
from importlib.metadata import PackageNotFoundError, version


@dataclass(frozen=True, slots=True)
class DiagnosticCheck:
    """One doctor check and its human-readable result."""

    label: str
    passed: bool
    details: str


def run_doctor_checks() -> tuple[DiagnosticCheck, ...]:
    """Run the v0.1 platform and OCR pipeline diagnostics."""

    checks: list[DiagnosticCheck] = []

    windows_supported = sys.platform == "win32" and sys.getwindowsversion().major >= 10
    checks.append(
        DiagnosticCheck(
            "Supported Windows",
            windows_supported,
            platform.platform(),
        )
    )

    try:
        from winrt.windows.media.ocr import OcrEngine

        languages = tuple(OcrEngine.available_recognizer_languages)
        checks.append(DiagnosticCheck("Windows.Media.Ocr", True, "Available"))
        checks.append(
            DiagnosticCheck(
                "Installed OCR languages",
                bool(languages),
                ", ".join(language.language_tag for language in languages) or "None",
            )
        )
        max_dimension = int(OcrEngine.max_image_dimension)
        checks.append(
            DiagnosticCheck(
                "Maximum image dimension",
                max_dimension > 0,
                f"{max_dimension} px",
            )
        )
    except Exception as error:  # noqa: BLE001
        checks.append(DiagnosticCheck("Windows.Media.Ocr", False, str(error)))
        checks.append(DiagnosticCheck("Installed OCR languages", False, "Unavailable"))
        checks.append(DiagnosticCheck("Maximum image dimension", False, "Unavailable"))

    try:
        import pypdfium2  # noqa: F401

        pdfium_version = version("pypdfium2")
        checks.append(
            DiagnosticCheck("PDF renderer", True, f"pypdfium2 {pdfium_version}")
        )
    except Exception as error:  # noqa: BLE001
        checks.append(DiagnosticCheck("PDF renderer", False, str(error)))

    try:
        import pypdfium2 as pdfium
        import pypdfium2.raw as pdfium_c

        from .renderer import pdfium_bitmap_to_software_bitmap

        pdf_bitmap = pdfium.PdfBitmap.new_native(
            1,
            1,
            pdfium_c.FPDFBitmap_BGRA,
        )
        try:
            software_bitmap, width, height = pdfium_bitmap_to_software_bitmap(
                pdf_bitmap
            )
            software_bitmap.close()
        finally:
            pdf_bitmap.close()
        checks.append(
            DiagnosticCheck(
                "Direct-RAM conversion",
                (width, height) == (1, 1),
                f"SoftwareBitmap {width}x{height}",
            )
        )
    except Exception as error:  # noqa: BLE001
        checks.append(DiagnosticCheck("Direct-RAM conversion", False, str(error)))

    checks.append(
        DiagnosticCheck(
            "Python",
            sys.version_info >= (3, 11),
            platform.python_version(),
        )
    )

    try:
        package_version = version("matnocr")
        checks.append(DiagnosticCheck("MatnOCR", True, package_version))
    except PackageNotFoundError as error:
        checks.append(DiagnosticCheck("MatnOCR", False, str(error)))

    return tuple(checks)
