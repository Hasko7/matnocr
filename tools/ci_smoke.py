"""Record CI capabilities and verify an independently installed wheel."""

import argparse
import importlib
import platform
import subprocess
import sys
import sysconfig
from importlib.metadata import version
from pathlib import Path


def print_diagnostics() -> None:
    print(f"Platform: {platform.platform()}")
    print(f"Python: {platform.python_version()}")
    print(f"Interpreter: {sys.executable}")
    print(f"PDFium package: {version('pypdfium2')}")
    try:
        from winrt.windows.media.ocr import OcrEngine

        tags = [
            language.language_tag
            for language in OcrEngine.available_recognizer_languages
        ]
        print(f"Installed OCR languages: {', '.join(tags) or 'none'}")
    except (ImportError, OSError, RuntimeError) as error:
        print(f"Windows OCR capability unavailable: {error}")


def smoke_test() -> None:
    package = importlib.import_module("matnocr")
    package_path = Path(package.__file__).resolve()
    if not package_path.is_relative_to(Path(sys.prefix).resolve()):
        raise RuntimeError(
            f"Expected a wheel in the fresh environment, got {package_path}"
        )
    print(f"Installed package: {package_path}")

    for arguments in (["--version"], ["ocr", "--help"], ["output", "--help"]):
        subprocess.run(
            [sys.executable, "-I", "-m", "matnocr", *arguments],
            check=True,
            timeout=30,
        )

    console = Path(sysconfig.get_path("scripts")) / "matnocr.exe"
    result = subprocess.run(
        [str(console), "--version"],
        check=True,
        capture_output=True,
        text=True,
        timeout=30,
    )
    if result.stdout.strip() != version("matnocr"):
        raise RuntimeError("Console entry point returned an unexpected version")
    print("Wheel and console smoke tests passed.")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--diagnostics-only", action="store_true")
    arguments = parser.parse_args()
    print_diagnostics()
    if not arguments.diagnostics_only:
        smoke_test()


if __name__ == "__main__":
    main()
