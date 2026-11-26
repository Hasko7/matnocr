"""Exercise the installed MatnOCR CLI with an isolated, synthetic PDF."""

import importlib
import os
import subprocess
import sys
import sysconfig
from importlib.metadata import version
from pathlib import Path
from tempfile import TemporaryDirectory


def make_pdf(path: Path) -> None:
    """Write a two-page PDF without using a source-tree or test dependency."""

    first = b"BT /F1 24 Tf 30 140 Td (MATNOCR FIRST 123) Tj ET"
    second = b"BT /F1 24 Tf 30 140 Td (MATNOCR SECOND 456) Tj ET"
    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R 4 0 R] /Count 2 >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 400 220] "
        b"/Resources << /Font << /F1 5 0 R >> >> /Contents 6 0 R >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 400 220] "
        b"/Resources << /Font << /F1 5 0 R >> >> /Contents 7 0 R >>",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
        b"<< /Length "
        + str(len(first)).encode()
        + b" >>\nstream\n"
        + first
        + b"\nendstream",
        b"<< /Length "
        + str(len(second)).encode()
        + b" >>\nstream\n"
        + second
        + b"\nendstream",
    ]
    data = bytearray(b"%PDF-1.4\n")
    offsets = [0]
    for index, obj in enumerate(objects, start=1):
        offsets.append(len(data))
        data.extend(f"{index} 0 obj\n".encode() + obj + b"\nendobj\n")
    xref = len(data)
    data.extend(f"xref\n0 {len(offsets)}\n0000000000 65535 f \n".encode())
    for offset in offsets[1:]:
        data.extend(f"{offset:010d} 00000 n \n".encode())
    data.extend(
        f"trailer\n<< /Size {len(offsets)} /Root 1 0 R >>\n"
        f"startxref\n{xref}\n%%EOF\n".encode()
    )
    path.write_bytes(data)


def main() -> None:
    package = importlib.import_module("matnocr")
    package_version = version("matnocr")
    package_path = Path(package.__file__).resolve()
    if not package_path.is_relative_to(Path(sys.prefix).resolve()):
        raise RuntimeError(
            f"MatnOCR is not installed in this environment: {package_path}"
        )

    console = Path(sysconfig.get_path("scripts")) / "matnocr.exe"
    if not console.is_file():
        raise RuntimeError(f"Console entry point is missing: {console}")

    with TemporaryDirectory(prefix="matnocr-cli-check-") as directory:
        root = Path(directory)
        pdf = root / "sample.pdf"
        make_pdf(pdf)
        env = os.environ.copy()
        env["MATNOCR_CONFIG_HOME"] = str(root / "config")
        env["NO_COLOR"] = "1"
        env["PYTHONUTF8"] = "1"

        def run(*args: str, success: bool = True) -> subprocess.CompletedProcess[str]:
            result = subprocess.run(
                [str(console), *args],
                capture_output=True,
                text=True,
                encoding="utf-8",
                env=env,
                timeout=60,
                check=False,
            )
            if (result.returncode == 0) != success:
                raise AssertionError(
                    f"Unexpected exit {result.returncode} for {args!r}:\n"
                    f"stdout: {result.stdout}\nstderr: {result.stderr}"
                )
            if not success and "Traceback (most recent call last)" in result.stderr:
                raise AssertionError(f"Uncaught traceback for {args!r}")
            return result

        assert run("--version").stdout.strip() == package_version
        for args in (
            ("--help",),
            ("ocr", "--help"),
            ("languages", "--help"),
            ("output", "--help"),
        ):
            assert "Usage" in run(*args).stdout
        assert "Ready" in run("doctor").stdout
        assert "en-US" in run("languages").stdout
        assert "en-US" in run("languages", "default", "en").stdout
        assert "md" in run("output", "default", "md").stdout
        assert "md" in run("output").stdout
        assert run(str(pdf), "--page-count").stdout.strip() == "2"

        quiet = run(
            str(pdf), "--lang", "en", "--pages", "2", "--quality", "fast", "--quiet"
        )
        assert not quiet.stdout and not quiet.stderr
        markdown = root / "sample_matnocr_en_200dpi.md"
        markdown_text = markdown.read_text(encoding="utf-8")
        assert "# Page 2" in markdown_text and "SECOND" in markdown_text.upper()
        assert "# Page 1" not in markdown_text

        text = root / "custom.txt"
        run(
            str(pdf),
            "--lang",
            "en-US",
            "--pages",
            "1",
            "--dpi",
            "300",
            "--no-layout",
            "--format",
            "txt",
            "-o",
            str(text),
        )
        text_content = text.read_text(encoding="utf-8")
        assert "Page 1" in text_content and "FIRST" in text_content.upper()
        assert "Page 2" not in text_content
        run(
            str(pdf),
            "--lang",
            "en",
            "--pages",
            "2",
            "--dpi",
            "200",
            "-o",
            str(text),
            success=False,
        )
        run(
            str(pdf),
            "--lang",
            "en",
            "--pages",
            "2",
            "--dpi",
            "200",
            "-o",
            str(text),
            "--force",
            "--quiet",
        )
        assert "SECOND" in text.read_text(encoding="utf-8").upper()

        for args in (
            (str(pdf), "--pages", "3"),
            (str(pdf), "--pages", "2-1"),
            (str(pdf), "--lang", "zz-ZZ"),
            (str(pdf), "--dpi", "123"),
            (str(pdf), "--format", "md", "-o", str(text)),
            (str(root / "missing.pdf"),),
        ):
            assert run(*args, success=False).stderr.strip()

        module = subprocess.run(
            [sys.executable, "-I", "-m", "matnocr", "--version"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            env=env,
            timeout=30,
            check=True,
        )
        assert module.stdout.strip() == package_version

    print(f"Full installed-wheel CLI check passed: {package_path}")


if __name__ == "__main__":
    main()
