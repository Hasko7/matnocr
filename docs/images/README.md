# README Screenshots

The project README includes these supplied screenshots:

| Filename | Contents |
| --- | --- |
| `terminal.png` | MatnOCR help and a real Arabic OCR run in Windows Terminal, with progress and a completion summary. |
| `book_page.png` | The Arabic book page headed الأمور بمقاصدها, matching the OCR excerpt in the README. |

The README uses relative image links. Keep these filenames when replacing the
images, or update the corresponding links in the root README.

## Arabic Book Example

The README shows the book page followed by the complete Markdown OCR output
supplied by the user. The run uses Arabic (`ar-SA`) at 300 DPI. `# Page 21`
refers to the PDF page; the printed page number visible on the scan is 24.

The excerpt is intentionally unedited, including OCR errors, line breaks,
paragraph spacing, and the recognized footnote. Do not silently correct words
when updating an OCR demonstration.

The public README book example is separate from the synthetic documents used
by the automated integration tests. Those tests continue to generate original
English, German, and Arabic examples locally; see
[the integration test notes](../../tests/integration/README.md).

## Updating Screenshots

1. Capture a real terminal run with readable text, showing the command and
   completion output. Crop unrelated windows and omit private paths.
2. Capture the matching book page with all relevant text visible.
3. If the page changes, replace the README excerpt with the actual OCR output
   for that same page and update its language, DPI, and page numbers.
4. Preview the root README in your editor or on GitHub. Check that both image
   paths resolve and that the book page can be compared with the OCR output.

Use PNG images and keep text sharp at the size displayed in the README.
