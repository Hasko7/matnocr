# Native Windows OCR PDF CLI – Project

## 1. Projektidee

Dieses Projekt ist eine sehr schnelle, vollständig lokale OCR-CLI für Windows.

Ziel ist es, gescannte PDF-Bücher und Dokumente direkt im Terminal in Text umzuwandeln – mit besonderem Fokus auf arabische Bücher, aber mit Unterstützung für alle OCR-Sprachen, die über die native Windows-OCR-Engine verfügbar sind.

Die Anwendung soll:

- vollständig lokal arbeiten
- keine Cloud-OCR benötigen
- ohne GPU funktionieren
- sehr schnell sein
- große PDFs verarbeiten können
- mehrere Sprachen unterstützen
- besonders gut für arabische Buchseiten funktionieren
- eine saubere und angenehme CLI bieten
- als Open-Source-Projekt auf GitHub veröffentlicht werden
- einfach über PyPI bzw. `uv tool` / `pipx` installierbar sein
- zusätzlich als fertiger Windows-Build über GitHub Releases angeboten werden

## 2. Aktueller technischer Kern

### OCR-Engine

Die eigentliche Texterkennung erfolgt über:

```python
Windows.Media.Ocr
```

Python greift über PyWinRT auf die native Windows Runtime API zu:

```python
from winrt.windows.media.ocr import OcrEngine
```

Vorteile:

- sehr schnelle lokale OCR
- kein separates großes KI-Modell
- Windows verwaltet die OCR-Sprachpakete
- offline verwendbar
- gute Qualität bei arabischem Buchdruck
- mehrere installierbare Sprachen

### Aktuell erkannte Windows-OCR-Sprachen auf dem Testsystem

```text
ar-SA
de-DE
tr-TR / tr
```

Windows unterstützt zusätzlich weitere OCR-Sprachen wie unter anderem:

```text
bg-BG
bs-LATN-BA
cs-CZ
da-DK
el-GR
en-GB
en-US
es-ES
es-MX
fi-FI
fr-CA
fr-FR
hr-HR
hu-HU
it-IT
ja-JP
ko-KR
nb-NO
nl-NL
pl-PL
pt-BR
pt-PT
ro-RO
ru-RU
sk-SK
sl-SI
sr-CYRL-RS
sr-LATN-RS
sv-SE
zh-CN
zh-HK
zh-TW
```

Die Anwendung soll nicht mit einer festen Sprachliste arbeiten, sondern die tatsächlich installierten Windows-OCR-Sprachen dynamisch über die Windows API abfragen.

## 3. Aktuelle Direct-RAM-Pipeline

Die erste Version schrieb jede gerenderte PDF-Seite als temporäre PNG-Datei auf die Festplatte.

Frühere Pipeline:

```text
PDF
→ PyMuPDF
→ RGB
→ PNG-Encoding
→ temporäre Datei
→ PNG erneut einlesen
→ BitmapDecoder
→ SoftwareBitmap
→ Windows OCR
```

Die aktuelle optimierte Pipeline arbeitet direkt im RAM:

```text
PDF
→ PDF Renderer
→ Pixel im RAM
→ SoftwareBitmap
→ Windows OCR
```

Dadurch entfallen:

- temporäre Bilddateien
- SSD-Schreibzugriffe
- erneutes Einlesen
- PNG-Encoding
- PNG-Decoding

Die OCR-Qualität blieb im Vergleich praktisch identisch, die Verarbeitung wurde jedoch schneller.

## 4. Aktueller PDF-Renderer

Der aktuelle Prototyp verwendet:

```python
PyMuPDF
```

PyMuPDF liefert sehr hohe Rendering-Geschwindigkeit und funktioniert mit der Direct-RAM-Pipeline sehr gut.

Vor einer öffentlichen Veröffentlichung muss jedoch die Lizenzstrategie bewusst entschieden werden, da PyMuPDF AGPL/commercial dual-lizenziert ist.

### Zu prüfende Alternative

```text
pypdfium2
```

`pypdfium2` verwendet Google PDFium und ist für ein permissiv lizenziertes Open-Source-Projekt interessant.

Es soll deshalb ein reproduzierbarer Benchmark durchgeführt werden:

```text
PyMuPDF Direct RAM
vs.
pypdfium2 Direct RAM
```

Verglichen werden:

- Rendering-Zeit
- Bitmap-/Buffer-Konvertierung
- gesamte OCR-Zeit
- Speicherverbrauch
- OCR-Ausgabe
- Verhalten bei 200 / 250 / 300 DPI
- Paketgröße
- Installationsaufwand
- Lizenzfolgen

Erst danach wird der endgültige PDF-Renderer festgelegt.

## 5. Aktuelle Performance

Getestet wurde eine sechsseitige gescannte arabische PDF.

### 200 DPI – Direct RAM

```text
Pages:      6
Total:      1.685 s
Average:    0.281 s/page
```

Breakdown:

```text
Rendering:  0.040 s/page
Bitmap:     0.015 s/page
OCR:        0.224 s/page
```

### 300 DPI – Direct RAM

```text
Pages:      6
Total:      2.137 s
Average:    0.356 s/page
```

Breakdown:

```text
Rendering:  0.032 s/page
Bitmap:     0.032 s/page
OCR:        0.291 s/page
```

### Alte 300-DPI-PNG-Pipeline

```text
Average: ca. 0.42 s/page
```

### Neue Direct-RAM-Version

```text
Average: ca. 0.356 s/page
```

Die Worterkennung blieb praktisch identisch.

## 6. DPI-Modi

Die Anwendung soll drei direkte DPI-Modi unterstützen:

```text
200 DPI
250 DPI
300 DPI
```

Zusätzlich sollen benutzerfreundliche Presets angeboten werden:

```text
fast      -> 200 DPI
balanced  -> 250 DPI
quality   -> 300 DPI
```

Geplanter Standard:

```text
quality / 300 DPI
```

300 DPI hat auf den bisherigen arabischen Buchseiten an mehreren schwierigen Stellen bessere Ergebnisse geliefert, bei weiterhin sehr hoher Geschwindigkeit.

## 7. Arabisch und RTL

Ein besonderer Fokus des Projekts liegt auf Arabisch.

Windows OCR liefert die erkannten Wörter inklusive Bounding Boxes. Bei RTL-Sprachen wird die Wortreihenfolge deshalb anhand der horizontalen Position rekonstruiert.

Aktuell vorgesehene RTL-Sprachen:

```text
ar
fa
ur
he
```

Die Sortierung geschieht pro erkannter Zeile.

### Beispiel

Windows-interne visuelle Reihenfolge:

```text
أو العبادات في ركن النية هل الشافعية أصحابنا اختلف الأول
```

rekonstruiert:

```text
الأول اختلف أصحابنا الشافعية هل النية ركن في العبادات أو
```

## 8. Geplantes CLI-Erlebnis

Die Anwendung soll nicht wie ein simples Python-Skript wirken, sondern wie eine professionelle moderne CLI.

Geplanter Stack:

```text
Typer
+
Rich
```

Typer soll übernehmen:

- Argument Parsing
- Subcommands
- Validation
- Help
- Shell Completion
- Typ-basierte Parameterdefinition

Rich soll übernehmen:

- Progress Bars
- Tabellen
- Panels
- Farben
- Statusmeldungen
- Erfolgs- und Fehlermeldungen
- saubere Zusammenfassungen

### Geplanter Standardaufruf

```powershell
nativeocr book.pdf
```

### Explizite Sprache und DPI

```powershell
nativeocr book.pdf --lang ar --dpi 300
```

### Seitenbereich

```powershell
nativeocr book.pdf --pages 30-50
```

### Mehrere Bereiche

```powershell
nativeocr book.pdf --pages 1,5,20-35,100
```

### Presets

```powershell
nativeocr book.pdf --quality fast
nativeocr book.pdf --quality balanced
nativeocr book.pdf --quality quality
```

### Eigene Ausgabe

```powershell
nativeocr book.pdf -o output.txt
```

### Ruhiger Modus für Skripte

```powershell
nativeocr book.pdf --quiet
```

## 9. Geplante Subcommands

### OCR

Standard:

```powershell
nativeocr book.pdf
```

### Sprachen anzeigen

```powershell
nativeocr languages
```

Beispiel:

```text
Installed OCR languages

✓ ar-SA    Arabic
✓ de-DE    German
✓ tr-TR    Turkish
```

Die Standardsprache für Aufrufe ohne `--lang` wird pro Windows-Benutzer
gespeichert:

```powershell
matnocr languages default ar-SA
```

MatnOCR zeigt nur die von Windows OCR bereitgestellten Sprachen an und verändert
keine Windows-Sprachpakete. Installation und Entfernung bleiben bewusst bei den
Windows-Einstellungen beziehungsweise einer administrativen PowerShell.

### Systemdiagnose

```powershell
nativeocr doctor
```

Mögliche Ausgabe:

```text
NativeOCR system check

✓ Windows supported
✓ Windows.Media.Ocr available
✓ OCR languages detected
✓ PDF renderer available
✓ Direct-RAM pipeline available
✓ Max OCR image dimension detected

Ready.
```

### Version

```powershell
nativeocr --version
```

## 10. Fehlerbehandlung

Die CLI soll verständliche Fehler erzeugen.

Beispiel bei fehlender OCR-Sprache:

```text
✗ Russian OCR language is not installed.

Detected OCR languages:
  ar-SA
  de-DE
  tr-TR

Install the Windows Russian OCR language capability and try again.
```

Die Anwendung soll niemals mit schwer verständlichen Python-Tracebacks enden, sofern es sich um normale Benutzerfehler handelt.

## 11. Ausgabeformate

### Version 1

Primär:

```text
TXT
```

Seitenmarker:

```text
========== Page 1 ==========

...

========== Page 2 ==========
```

### Spätere Versionen

Geplant bzw. denkbar:

```text
Markdown
JSON
JSONL
```

JSON könnte später enthalten:

- Seitenzahl
- Zeilentext
- Wörter
- Bounding Boxes
- Sprache
- DPI
- Timing-Informationen

## 12. Roh-OCR vs. Nachbearbeitung

Die Standardausgabe soll möglichst nah am echten OCR-Ergebnis bleiben.

Automatische sprachliche Korrekturen sollen nicht still im Hintergrund stattfinden.

Spätere optionale Modi können z. B. sein:

```powershell
--clean
--normalize-arabic
```

Mögliche Funktionen:

- Unicode-BiDi-Steuerzeichen entfernen
- offensichtliche Artefakte entfernen
- optionale Normalisierung von `ﷺ`
- Leerzeichenbereinigung
- Zeilenbereinigung

Wichtig:

```text
raw OCR
```

und:

```text
postprocessed OCR
```

müssen klar unterscheidbar bleiben.

## 13. Geplanter Python-Projektstack

### Runtime

```text
Python >= 3.11
```

### Paket- und Projektmanagement

```text
uv
```

### Build Backend

Vorgesehen:

```text
uv_build
```

### CLI

```text
Typer
Rich
```

### OCR

```text
PyWinRT
Windows.Media.Ocr
```

### PDF

Zu entscheiden:

```text
PyMuPDF
oder
pypdfium2
```

### Tests

```text
pytest
coverage.py
```

### Linting / Formatting

```text
Ruff
```

### Type Checking

Vorgesehen:

```text
ty
```

## 14. Geplante Projektstruktur

```text
project/
├── pyproject.toml
├── uv.lock
├── README.md
├── LICENSE
├── CHANGELOG.md
├── CONTRIBUTING.md
├── SECURITY.md
├── CODE_OF_CONDUCT.md
├── PROJECT.md
├── TODO.md
│
├── src/
│   └── nativeocr/
│       ├── __init__.py
│       ├── __main__.py
│       ├── cli.py
│       ├── engine.py
│       ├── renderer.py
│       ├── languages.py
│       ├── pages.py
│       ├── rtl.py
│       ├── output.py
│       ├── config.py
│       └── ui.py
│
├── tests/
│   ├── unit/
│   │   ├── test_pages.py
│   │   ├── test_languages.py
│   │   ├── test_rtl.py
│   │   └── test_output.py
│   │
│   └── integration/
│       ├── test_windows_ocr.py
│       └── test_pdf_renderer.py
│
└── .github/
    ├── ISSUE_TEMPLATE/
    ├── pull_request_template.md
    └── workflows/
        ├── ci.yml
        ├── release.yml
        └── codeql.yml
```

Der tatsächliche Paketname `nativeocr` ist hier nur ein Platzhalter. Der endgültige Projektname muss zuerst gewählt werden.

## 15. Packaging und Installation

Das Projekt soll als echtes Python-Paket gebaut werden.

Geplanter Console Entry Point:

```toml
[project.scripts]
PROJECTNAME = "package.cli:app"
```

Dadurch wird aus:

```powershell
python ocr.py book.pdf
```

später:

```powershell
PROJECTNAME book.pdf
```

## 16. Installation für Nutzer

### Empfohlen für technisch versierte Nutzer

```powershell
uv tool install PROJECTNAME
```

### Alternative

```powershell
pipx install PROJECTNAME
```

### Klassisches pip

```powershell
pip install PROJECTNAME
```

### Direkter Test von GitHub

```powershell
uv tool install git+https://github.com/USER/PROJECT.git
```

## 17. Windows-Binary / GitHub Release

Zusätzlich zum Python-Paket soll ein fertiger Windows-Build angeboten werden.

Geplant:

```text
PROJECTNAME-windows-x64.zip
```

und eventuell:

```text
PROJECTNAME-windows-x64.exe
```

Für Version 1 soll zunächst PyInstaller getestet werden.

Zu prüfen:

```text
PyInstaller onedir
PyInstaller onefile
```

Später optional:

```text
Nuitka
```

Ziel ist, dass normale Windows-Nutzer die Anwendung ohne eigene Python-Installation verwenden können.

## 18. GitHub und Open Source

Das Projekt soll öffentlich auf GitHub veröffentlicht werden.

Geplante Repository-Dateien:

```text
README.md
LICENSE
CONTRIBUTING.md
CHANGELOG.md
SECURITY.md
CODE_OF_CONDUCT.md
PROJECT.md
TODO.md
```

Zusätzlich:

```text
.github/
```

mit:

- CI Workflows
- Release Workflow
- CodeQL
- Issue Templates
- Pull Request Template
- Dependabot-Konfiguration

## 19. CI – Continuous Integration

CI soll über GitHub Actions laufen.

Da die OCR Windows-spezifisch ist, muss mindestens ein Windows-Runner verwendet werden.

Geplanter Ablauf bei Pull Requests und Pushes:

```text
Checkout
→ setup uv
→ install Python
→ uv sync --locked
→ Ruff check
→ Ruff format --check
→ ty check
→ pytest
→ build wheel/sdist
→ install built package
→ CLI smoke test
```

### Python-Matrix

Geplant zu prüfen:

```text
3.11
3.12
3.13
3.14
```

Nur Versionen, die mit allen WinRT-Abhängigkeiten stabil funktionieren, sollen offiziell unterstützt werden.

## 20. Tests

### Unit Tests

Sollen unabhängig von installierten Windows-Sprachpaketen funktionieren.

Zu testen:

- Page-Range-Parser
- Language-Resolution
- RTL-Sortierung
- Output-Dateinamen
- Presets
- Config
- CLI Validation
- Textformatierung

### Integration Tests

Separat:

- Windows.Media.Ocr verfügbar
- SoftwareBitmap-Konvertierung
- echter OCR-Lauf
- PDF-Rendering
- Direct-RAM-Pipeline
- installierte Sprachpakete

Integrationstests müssen berücksichtigen, dass GitHub Windows Runner nicht zwingend dieselben OCR-Sprachen installiert haben wie ein normaler Windows-11-PC.

## 21. Releases

Vorgesehener Release-Ablauf:

```text
main
↓
Git Tag
↓
v0.x.y
↓
GitHub Actions
↓
Tests
↓
Python Build
↓
Windows Binary Build
↓
PyPI
↓
GitHub Release
```

Alle Artefakte einer Version sollen aus exakt demselben Git-Tag stammen.

## 22. PyPI

Das Projekt soll später auf PyPI veröffentlicht werden.

Beispiel:

```powershell
uv tool install PROJECTNAME
```

Der PyPI-Release soll möglichst über Trusted Publishing / OIDC erfolgen, sodass keine langfristigen PyPI-API-Tokens als GitHub Secrets gespeichert werden müssen.

## 23. GitHub Releases

GitHub Releases sollen zusätzlich bereitstellen:

```text
Python wheel
sdist
Windows x64 binary / zip
checksums
release notes
```

Später eventuell:

```text
Windows ARM64
```

## 24. Lizenzstrategie

Die Lizenz muss vor dem ersten öffentlichen Release bewusst entschieden werden.

Zwei denkbare Richtungen:

### PyMuPDF behalten

Dann muss die AGPL-Lizenzsituation berücksichtigt werden.

Mögliche Projektlizenz:

```text
AGPL-3.0
```

### pypdfium2 verwenden

Dann wäre ein permissiveres Projektmodell einfacher möglich, z. B.:

```text
MIT
```

oder:

```text
Apache-2.0
```

Die endgültige Entscheidung erfolgt erst nach Renderer-Benchmark und Lizenzprüfung.

## 25. Projektname

Der aktuelle Name ist noch nicht festgelegt.

Der endgültige Name sollte:

- kurz sein
- gut aussprechbar sein
- als CLI-Befehl funktionieren
- nicht bereits auf PyPI belegt sein
- nicht mit bestehenden GitHub-Projekten kollidieren
- idealerweise OCR / PDF / native Windows / Geschwindigkeit vermitteln
- auch für nicht-arabische Nutzer funktionieren
- nicht zu stark nur auf Arabisch beschränkt sein

Vor Festlegung müssen mindestens geprüft werden:

```text
PyPI
GitHub
winget
npm
Cargo
Suchmaschinen
```

Der Name `winocr` soll nicht verwendet werden, da bereits Projekte mit diesem Namen existieren.

## 26. Positionierung

Das Projekt soll nicht nur als einfacher Wrapper um Windows OCR positioniert werden.

Die eigentliche Nische ist:

```text
High-performance PDF/book OCR CLI powered by Windows native OCR
```

Besondere Merkmale:

- PDF-first
- book-first
- Arabic-first, aber multilingual
- native Windows OCR
- Direct RAM
- RTL reconstruction
- Page ranges
- DPI presets
- sehr hoher Durchsatz
- vollständig lokal
- keine GPU
- angenehme CLI
- reproduzierbare Benchmarks

## 27. Version 0.1 – Zielumfang

Die erste echte Open-Source-Version soll bewusst kompakt bleiben.

Geplant:

- PDF-Eingabe
- Windows OCR
- Direct-RAM-Pipeline
- dynamische Windows-OCR-Sprachen
- Arabic / RTL-Rekonstruktion
- `--lang`
- `--pages`
- `--dpi`
- `--quality`
- `--output`
- TXT-Ausgabe
- `languages`
- `doctor`
- `--quiet`
- `--version`
- Rich Progress
- saubere Fehlermeldungen
- Python Package
- GitHub CI
- PyPI Release
- GitHub Windows Release

Noch nicht zwingend in v0.1:

- GUI
- KI-Korrektur
- Tesseract-Ensemble
- komplexe Layout-Rekonstruktion
- Markdown-Layout
- OCR-Server
- parallele OCR
- Batch-Ordnerverarbeitung

## 28. Version 0.2+ – mögliche Erweiterungen

### Erweiterte Ausgabe

- Markdown
- JSON
- JSONL
- Bounding Boxes

### Batch-Verarbeitung

```powershell
PROJECTNAME batch ./books
```

### Resume

Abgebrochene große OCR-Jobs fortsetzen.

### Benchmark Command

```powershell
PROJECTNAME benchmark book.pdf
```

### Renderer Benchmark

PyMuPDF / PDFium vergleichen.

### Alternative OCR Engines

Optional:

- Tesseract
- Windows OCR + Tesseract Ensemble
- Fallback-Engine für schwierige Seiten

### Arabische Nachbearbeitung

Optional:

- ﷺ-Normalisierung
- BiDi-Cleanup
- Unicode-Normalisierung
- Artefakterkennung

### Strukturierte Ausgabe

- Überschriften
- Fußnoten
- Seitenzahlen
- Absätze
- Tabellen

## 29. Benchmark-Regeln

Performance-Vergleiche sollen reproduzierbar sein.

Für jeden Test dokumentieren:

- PDF
- Seitenzahl
- DPI
- CPU
- Windows-Version
- Python-Version
- Renderer
- OCR Engine
- Render-Zeit
- Bitmap-Zeit
- OCR-Zeit
- Gesamtzeit
- durchschnittliche Zeit pro Seite

Urheberrechtlich geschützte Testseiten sollen nicht ohne Erlaubnis in das öffentliche Repository aufgenommen werden.

Für CI-Tests sollen stattdessen eigene oder Public-Domain-Testdokumente verwendet werden.

## 30. Langfristige Vision

Das langfristige Ziel ist eine Open-Source-Windows-CLI, mit der ein Nutzer beispielsweise nur Folgendes ausführen muss:

```powershell
PROJECTNAME kitab.pdf --lang ar --pages 30-100
```

und innerhalb kurzer Zeit eine saubere Textdatei erhält.

Das Projekt soll die Einfachheit einer modernen CLI mit der Geschwindigkeit der nativen Windows-OCR-Engine verbinden.

Langfristige Kernprinzipien:

```text
fast
local
simple
transparent
multilingual
scriptable
open source
```
