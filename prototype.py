import argparse
import asyncio
import time
from pathlib import Path
from statistics import median

import pypdfium2 as pdfium
import pypdfium2.raw as pdfium_c
from winrt.windows.globalization import Language
from winrt.windows.graphics.imaging import (
    BitmapPixelFormat,
    SoftwareBitmap,
)
from winrt.windows.media.ocr import OcrEngine
from winrt.windows.storage.streams import DataWriter


RTL_LANGUAGES = {"ar", "fa", "ur", "he"}
MIN_PAGE_COVERAGE = 0.70


# ============================================================
# LANGUAGE
# ============================================================

def resolve_language(requested: str) -> str:
    requested = requested.lower()

    languages = list(
        OcrEngine.available_recognizer_languages
    )

    for lang in languages:
        if lang.language_tag.lower() == requested:
            return lang.language_tag

    for lang in languages:
        if (
            lang.language_tag
            .lower()
            .startswith(requested + "-")
        ):
            return lang.language_tag

    available = ", ".join(
        lang.language_tag
        for lang in languages
    )

    raise RuntimeError(
        f"OCR language '{requested}' "
        f"is not installed. "
        f"Installed: {available}"
    )


def is_rtl(language_tag: str) -> bool:
    return (
        language_tag
        .lower()
        .split("-")[0]
        in RTL_LANGUAGES
    )


# ============================================================
# TEXT
# ============================================================

def reconstruct_text(
    result,
    rtl: bool,
    preserve_layout: bool = True,
) -> str:
    lines = []

    for line in result.lines:
        words = list(line.words)

        if rtl:
            words.sort(
                key=lambda w: (
                    w.bounding_rect.x
                    + w.bounding_rect.width
                ),
                reverse=True,
            )
        else:
            words.sort(
                key=lambda w:
                    w.bounding_rect.x
            )

        text = " ".join(
            w.text
            for w in words
        )

        if not preserve_layout or not words:
            lines.append(text)
            continue

        top = min(
            w.bounding_rect.y
            for w in words
        )
        bottom = max(
            w.bounding_rect.y
            + w.bounding_rect.height
            for w in words
        )

        lines.append(
            (
                text,
                top,
                bottom,
                bottom - top,
            )
        )

    if not preserve_layout:
        return " ".join(
            line
            for line in lines
            if line
        )

    if not lines:
        return ""

    gaps = [
        max(
            0.0,
            lines[index + 1][1]
            - lines[index][2],
        )
        for index in range(len(lines) - 1)
    ]
    heights = [
        height
        for _, _, _, height in lines
        if height > 0
    ]

    if gaps and heights:
        if len(gaps) == 1:
            paragraph_gap = median(heights) * 0.8
        else:
            ordered_gaps = sorted(gaps)
            normal_gap = median(
                ordered_gaps[
                    :max(1, (len(ordered_gaps) + 1) // 2)
                ]
            )
            paragraph_gap = max(
                median(heights) * 0.8,
                normal_gap * 1.8,
            )
    else:
        paragraph_gap = float("inf")

    output = []

    for index, line in enumerate(lines):
        output.append(line[0])

        if (
            index < len(gaps)
            and gaps[index] > paragraph_gap
        ):
            output.append("")

    return "\n".join(output)


# ============================================================
# FIND SCAN IMAGE
# ============================================================

def find_dominant_image(page):
    page_area = (
        page.get_width()
        * page.get_height()
    )

    if page_area <= 0:
        return None, 0.0

    best_image = None
    best_coverage = 0.0

    for image in page.get_objects(
        filter=[
            pdfium_c.FPDF_PAGEOBJ_IMAGE
        ]
    ):
        try:
            left, bottom, right, top = (
                image.get_bounds()
            )

            area = (
                max(0.0, right - left)
                * max(0.0, top - bottom)
            )

            coverage = (
                area / page_area
            )

            if coverage > best_coverage:
                best_image = image
                best_coverage = coverage

        except Exception:
            pass

    return best_image, best_coverage


# ============================================================
# PDFIUM BITMAP -> WINDOWS BITMAP
# ============================================================

def pdfium_bitmap_to_software_bitmap(
    pdf_bitmap,
):
    width = pdf_bitmap.width
    height = pdf_bitmap.height

    if pdf_bitmap.mode != "BGRA":
        raise RuntimeError(
            f"Unsupported PDFium bitmap mode: "
            f"{pdf_bitmap.mode}"
        )

    row_bytes = width * 4

    raw = bytes(
        pdf_bitmap.buffer
    )

    # Normalerweise nicht nötig,
    # aber sicher für Bitmap-Padding.
    if pdf_bitmap.stride != row_bytes:
        packed = bytearray(
            row_bytes * height
        )

        for y in range(height):
            src = (
                y * pdf_bitmap.stride
            )

            dst = (
                y * row_bytes
            )

            packed[
                dst:dst + row_bytes
            ] = raw[
                src:src + row_bytes
            ]

        raw = bytes(packed)

    writer = DataWriter()

    writer.write_bytes(raw)

    buffer = writer.detach_buffer()

    writer.close()

    software_bitmap = (
        SoftwareBitmap.create_copy_from_buffer(
            buffer,
            BitmapPixelFormat.BGRA8,
            width,
            height,
        )
    )

    return (
        software_bitmap,
        width,
        height,
    )


# ============================================================
# ORIGINAL SCAN -> TARGET DPI
# ============================================================

def original_image_at_dpi(
    image,
    dpi: int,
):
    """
    Rendert nur das eingebettete Scanbild
    direkt auf die gewünschte DPI.

    Keine komplette PDF-Seite.
    Kein Pillow.
    Keine temporäre Datei.
    """

    original_matrix = (
        image.get_matrix()
    )

    scale = (
        dpi / 72.0
    )

    image.set_matrix(
        original_matrix.scale(
            scale,
            scale,
        )
    )

    try:
        pdf_bitmap = (
            image.get_bitmap(
                render=True,
                scale_to_original=False,
            )
        )

    finally:
        image.set_matrix(
            original_matrix
        )

    try:
        return (
            pdfium_bitmap_to_software_bitmap(
                pdf_bitmap
            )
        )

    finally:
        pdf_bitmap.close()


# ============================================================
# FALLBACK
# ============================================================

def render_page_at_dpi(
    page,
    dpi: int,
):
    """
    Fallback für PDFs ohne großes Scanbild.
    """

    pdf_bitmap = page.render(
        scale=dpi / 72.0,
        optimize_mode="print",
        no_smoothimage=True,
        force_bitmap_format=(
            pdfium_c.FPDFBitmap_BGRA
        ),
        fill_color=(
            255,
            255,
            255,
            255,
        ),
    )

    try:
        return (
            pdfium_bitmap_to_software_bitmap(
                pdf_bitmap
            )
        )

    finally:
        pdf_bitmap.close()


# ============================================================
# OCR
# ============================================================

async def run_ocr(
    pdf_path: Path,
    language_tag: str,
    dpi: int,
    preserve_layout: bool = True,
):
    engine = (
        OcrEngine.try_create_from_language(
            Language(
                language_tag
            )
        )
    )

    if engine is None:
        raise RuntimeError(
            f"Could not create Windows OCR "
            f"engine for {language_tag}"
        )

    rtl = is_rtl(
        language_tag
    )

    print()
    print("MatnOCR PDFium DPI test")
    print("-----------------------")
    print(f"PDF:       {pdf_path}")
    print(f"Language:  {language_tag}")
    print(f"DPI:       {dpi}")
    print(
        f"Direction: "
        f"{'RTL' if rtl else 'LTR'}"
    )
    print("Pipeline:  Direct RAM")
    print()

    output = []

    total_bitmap = 0.0
    total_ocr = 0.0

    original_pages = 0
    rendered_pages = 0

    total_start = (
        time.perf_counter()
    )

    with pdfium.PdfDocument(
        pdf_path
    ) as pdf:

        page_count = len(pdf)

        for page_index in range(
            page_count
        ):
            page = pdf[
                page_index
            ]

            page_start = (
                time.perf_counter()
            )

            image, coverage = (
                find_dominant_image(
                    page
                )
            )

            use_original = (
                image is not None
                and coverage
                >= MIN_PAGE_COVERAGE
            )

            # --------------------------------
            # Bitmap
            # --------------------------------

            t = time.perf_counter()

            if use_original:
                try:
                    (
                        software_bitmap,
                        width,
                        height,
                    ) = original_image_at_dpi(
                        image,
                        dpi,
                    )

                    mode = "ORIGINAL"

                    original_pages += 1

                except RuntimeError:
                    (
                        software_bitmap,
                        width,
                        height,
                    ) = render_page_at_dpi(
                        page,
                        dpi,
                    )

                    mode = "RENDER"

                    rendered_pages += 1

            else:
                (
                    software_bitmap,
                    width,
                    height,
                ) = render_page_at_dpi(
                    page,
                    dpi,
                )

                mode = "RENDER"

                rendered_pages += 1

            bitmap_time = (
                time.perf_counter()
                - t
            )

            total_bitmap += (
                bitmap_time
            )

            # --------------------------------
            # Windows OCR limit
            # --------------------------------

            if (
                width
                > OcrEngine.max_image_dimension
                or height
                > OcrEngine.max_image_dimension
            ):
                software_bitmap.close()
                page.close()

                raise RuntimeError(
                    f"Page {page_index + 1}: "
                    f"{width}x{height} exceeds "
                    f"Windows OCR limit "
                    f"{OcrEngine.max_image_dimension}"
                )

            # --------------------------------
            # OCR
            # --------------------------------

            t = time.perf_counter()

            result = (
                await engine.recognize_async(
                    software_bitmap
                )
            )

            ocr_time = (
                time.perf_counter()
                - t
            )

            total_ocr += (
                ocr_time
            )

            software_bitmap.close()

            # --------------------------------
            # Text
            # --------------------------------

            text = reconstruct_text(
                result,
                rtl,
                preserve_layout,
            )

            elapsed = (
                time.perf_counter()
                - page_start
            )

            print(
                f"Page {page_index + 1}: "
                f"{elapsed:.3f}s "
                f"[{mode}] "
                f"{width}x{height} "
                f"[bitmap={bitmap_time:.3f} "
                f"| OCR={ocr_time:.3f}]"
            )

            output.append(
                f"\n========== "
                f"Page {page_index + 1} "
                f"==========\n\n"
                f"{text.strip()}\n"
            )

            page.close()

    # ========================================================
    # SUMMARY
    # ========================================================

    total = (
        time.perf_counter()
        - total_start
    )

    lang_short = (
        language_tag
        .split("-")[0]
        .lower()
    )

    output_path = (
        pdf_path.with_name(
            f"{pdf_path.stem}"
            f"_pdfium_"
            f"{lang_short}_"
            f"{dpi}dpi.txt"
        )
    )

    output_path.write_text(
        "".join(output),
        encoding="utf-8",
    )

    print()
    print("Summary")
    print("-------")

    print(
        f"Pages:          "
        f"{page_count}"
    )

    print(
        f"Original scan:  "
        f"{original_pages}"
    )

    print(
        f"Rendered:       "
        f"{rendered_pages}"
    )

    print(
        f"Total:          "
        f"{total:.3f}s"
    )

    print(
        f"Average:        "
        f"{total / page_count:.3f}s/page"
    )

    print(
        f"Bitmap:         "
        f"{total_bitmap / page_count:.3f}s/page"
    )

    print(
        f"OCR:            "
        f"{total_ocr / page_count:.3f}s/page"
    )

    print()

    print(
        f"Saved: "
        f"{output_path}"
    )


# ============================================================
# CLI
# ============================================================

def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "pdf"
    )

    parser.add_argument(
        "--lang",
        default="ar",
    )

    parser.add_argument(
        "--dpi",
        type=int,
        default=300,
        choices=(
            200,
            250,
            300,
        ),
    )

    parser.add_argument(
        "--no-layout",
        action="store_true",
        help=(
            "Ignore line and paragraph layout "
            "and join the text continuously."
        ),
    )

    return parser.parse_args()


async def main():
    args = parse_args()

    pdf_path = Path(
        args.pdf
    ).resolve()

    if not pdf_path.exists():
        raise FileNotFoundError(
            pdf_path
        )

    language_tag = (
        resolve_language(
            args.lang
        )
    )

    await run_ocr(
        pdf_path,
        language_tag,
        args.dpi,
        not args.no_layout,
    )


if __name__ == "__main__":
    asyncio.run(main())
