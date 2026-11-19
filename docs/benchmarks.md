# Benchmarks

[Back to the README](../README.md)

Historical local results from the earlier **PyMuPDF Direct-RAM prototype**,
using a six-page scanned Arabic PDF:

| Resolution | Total time | Time per page |
| --- | --- | --- |
| 200 DPI | 1.685 s | 0.281 s |
| 300 DPI | 2.137 s | 0.356 s |

These values do not measure the current pypdfium2 package version and are not
a general performance guarantee. According to the roadmap, the renderer
comparison at 200/250/300 DPI is complete; pypdfium2 was selected with
practically comparable OCR quality. Memory usage, wheel size, and a complete
release benchmark with hardware details remain pending.
See [PROJECT.md](../PROJECT.md) for more background.

