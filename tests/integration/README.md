# Integration Test Documents

Run these tests on Windows:

```powershell
uv run pytest -m integration
```

All test text is original and stored in the test code. PDFs and intermediate
images are created under pytest's temporary directory. No private book pages,
downloaded texts, or font files are committed.

## Documents

- **English:** a small PDF with standard Helvetica text, built directly from
  original ASCII PDF content. It tests full-page rendering and basic OCR.
- **German:** an image-only PDF containing umlauts and eszett, including
  `Schüler`, `Bücher`, `Grüße`, and `Straße`.
- **Arabic:** an image-only PDF with three original lines, including
  `هذا كتاب مفيد` and `العلم نور والعمل خير`. Assertions check anchor words
  in logical reading order, covering word order within and across lines.

The Unicode scans are rendered by `render_test_text.ps1` using Windows
System.Drawing and the locally installed Arial font. Windows shapes the Arabic
text, and the script sets right-to-left reading direction. Only the resulting
image is embedded in the PDF; there is no text layer to bypass OCR. Tests also
verify the absence of hidden PDF text and the embedded image dimensions.
Temporary JPEGs are used only to construct the test inputs; the application's
Direct-RAM OCR pipeline is unchanged. No extra Python dependency is required.

## Missing Capabilities

- PDFium tests skip when pypdfium2 is not installed.
- Windows-dependent tests skip outside Windows or when the required WinRT
  module is missing.
- English, German, and Arabic OCR tests skip independently if their Windows
  OCR language pack is absent. Tests never install or remove language packs.
- Unicode scan generation skips if Windows PowerShell, System.Drawing, or
  Arial is unavailable. Rendering failures and the 30-second rendering timeout
  fail the test rather than silently skipping it.

Assertions tolerate punctuation and whitespace differences, but require the
chosen words and their order. New OCR differences should be investigated by
inspecting the generated page and actual OCR output before changing assertions.
The German and Arabic pages were visually checked after rendering with Poppler.

Public-domain texts can be used for future fixtures, but are not required for
these short original examples. Keep copyrighted book scans and private
benchmark documents out of the repository.
